# Kali Agents Usage Examples

## Quick Start Commands

### Network Reconnaissance
```bash
# Basic network scan
kali-agents recon 192.168.1.0/24

# Stealth scan with custom ports  
kali-agents recon target.com --type stealth --ports "22,80,443,3389"

# Aggressive scan with all features
kali-agents recon company.com --type aggressive --output results.json
```

### Web Application Testing
```bash
# Basic web assessment
kali-agents web https://target.com

# Deep assessment with custom wordlist
kali-agents web https://app.company.com --deep --wordlist big

# Comprehensive web pentest with output
kali-agents web https://api.company.com --deep --output webapp_results/
```

### Full Penetration Testing
```bash
# Basic pentest
kali-agents pentest target.com

# Comprehensive pentest with custom scope
kali-agents pentest company.com --scope full --format pdf

# Custom pentest excluding certain tests
kali-agents pentest client.com --scope custom --exclude "social,forensics"
```

### OSINT Research
```bash
# Person investigation
kali-agents osint "John Doe" --type person --depth deep

# Company intelligence gathering
kali-agents osint "ACME Corp" --type company --sources "shodan,maltego"

# Domain research with output
kali-agents osint company.com --type domain --output osint_report.json
```

### Digital Forensics
```bash
# Memory dump analysis
kali-agents forensics memory_dump.mem --type memory

# Suspicious file analysis
kali-agents forensics suspicious.exe --type file

# Network traffic analysis
kali-agents forensics capture.pcap --type network
```

### Interactive Mode
```bash
# Enter interactive mode
kali-agents interactive

# Example natural language commands:
# "Scan 192.168.1.1 for open ports"
# "Test website security for https://example.com" 
# "Perform OSINT research on John Doe"
# "Analyze memory dump /path/to/dump.mem"
```

### System Management
```bash
# Check system status
kali-agents status

# Run demonstration
kali-agents demo

# Interactive demonstration
kali-agents demo --interactive
```

## Advanced Usage

### Custom Configurations
```bash
# Use custom configuration file
export KALI_AGENTS_CONFIG=/path/to/custom.env
kali-agents pentest target.com

# Set custom output directory
kali-agents pentest target.com --output-dir /custom/path/

# Custom report formats
kali-agents pentest target.com --format html
kali-agents pentest target.com --format json
```

### Integration Examples
```bash
# Automated scanning with cron
0 2 * * * /path/to/kali-agents recon internal_network.com --output /var/log/scans/

# Pipeline integration
kali-agents recon $TARGET | jq '.hosts | keys[]' | xargs -I {} kali-agents web https://{}

# Custom scripting
for target in $(cat targets.txt); do
    kali-agents pentest $target --scope basic --output results/$target/
done
```
