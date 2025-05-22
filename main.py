import requests
from bs4 import BeautifulSoup
import re
import json

URL = "https://docs.aws.amazon.com/guardduty/latest/ug/runtime-monitoring-agent-release-history.html"

def fetch_guardduty_digests():
    r = requests.get(URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    result = {
        "fargate_ecs": {},
        "eks": {}
    }
    
    # Find Fargate ECS section
    fargate_section = soup.find('awsui-expandable-section', {'id': 'ecs-gdu-agent-release-history'})
    if fargate_section:
        print("Found Fargate section")
        current_version = None
        current_arch = None
        
        for tr in fargate_section.find_all('tr'):

            # Go over rows in fargate section table
            # first row is header, so skip it
            if tr.find('th'):
                continue

            # Go over columns in row
            tds = tr.find_all('td')
            if len(tds) >= 2:
                # First column contains version
                version_match = re.search(r'v\d+\.\d+\.\d+', tds[0].text)
                if version_match:
                    current_version = version_match.group(0)
                
                # Second column contains architecture and SHA256
                arch_text = tds[1].text
                if 'x86_64' in arch_text or 'AMD64' in arch_text:
                    sha256_match = re.search(r'sha256:[a-f0-9]{64}', arch_text)
                    if sha256_match and current_version:
                        key = f"{current_version}-Fg_x86_64"
                        result["fargate_ecs"][key] = sha256_match.group(0)
                
                if 'Graviton' in arch_text or 'ARM64' in arch_text:
                    sha256_match = re.search(r'sha256:[a-f0-9]{64}', arch_text)
                    if sha256_match and current_version:
                        key = f"{current_version}-Fg_arm64"
                        result["fargate_ecs"][key] = sha256_match.group(0)

    # Find EKS section
    eks_section = soup.find('awsui-expandable-section', {'id': 'eks-runtime-monitoring-agent-release-history'})
    if eks_section:
        print("Found EKS section")
        current_version = None
        
        for tr in eks_section.find_all('tr'):
            # Skip header row
            if tr.find('th'):
                continue

            # Go over columns in row
            tds = tr.find_all('td')
            if len(tds) >= 2:
                # First column contains version
                version_match = re.search(r'v\d+\.\d+\.\d+', tds[0].text)
                if version_match:
                    current_version = version_match.group(0)
                
                # Second column contains architecture and SHA256
                arch_text = tds[1].text
                if 'x86_64' in arch_text or 'AMD64' in arch_text:
                    sha256_match = re.search(r'sha256:[a-f0-9]{64}', arch_text)
                    if sha256_match and current_version:
                        key = f"{current_version}-Eks_x86_64"
                        result["eks"][key] = sha256_match.group(0)
                
                if 'Graviton' in arch_text or 'ARM64' in arch_text:
                    sha256_match = re.search(r'sha256:[a-f0-9]{64}', arch_text)
                    if sha256_match and current_version:
                        key = f"{current_version}-Eks_arm64"
                        result["eks"][key] = sha256_match.group(0)

    return result

if __name__ == "__main__":
    digests = fetch_guardduty_digests()
    with open('result/guardduty_runtime_image_sha256.json', 'w') as f:
        json.dump(digests, f, indent=2)
    