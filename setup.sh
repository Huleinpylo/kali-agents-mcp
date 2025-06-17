#!/bin/bash

# Kali Agents MCP - Automated Setup Script
# "At Your Service" - Complete system installation and configuration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Unicode symbols
CHECKMARK="✅"
CROSSMARK="❌"
ARROW="➡️"
STAR="⭐"
ROCKET="🚀"
GEAR="⚙️"
SHIELD="🛡️"

# Banner function
print_banner() {
    echo -e "${RED}"
    echo "██╗  ██╗ █████╗ ██╗     ██╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗███████╗"
    echo "██║ ██╔╝██╔══██╗██║     ██║    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝"
    echo "█████╔╝ ███████║██║     ██║    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ███████╗"
    echo "██╔═██╗ ██╔══██║██║     ██║    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ╚════██║"
    echo "██║  ██╗██║  ██║███████╗██║    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ███████║"
    echo "╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝"
    echo -e "${NC}"
    echo -e "${CYAN}                            'AT YOUR SERVICE'${NC}"
    echo -e "${YELLOW}                    Intelligent Cybersecurity Automation${NC}"
    echo ""
}

# Logging functions
log_info() {
    echo -e "${BLUE}${ARROW} $1${NC}"
}

log_success() {
    echo -e "${GREEN}${CHECKMARK} $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}${CROSSMARK} $1${NC}"
}

log_step() {
    echo -e "${PURPLE}${GEAR} $1${NC}"
}

# Check if running as root (not recommended)
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root is not recommended for security reasons"
        log_warning "Consider running as a regular user instead"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "Setup cancelled"
            exit 1
        fi
    fi
}

# Check system requirements
check_requirements() {
    log_step "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_success "Linux OS detected"
        
        # Check if Kali Linux
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            if [[ "$ID" == "kali" ]]; then
                log_success "Kali Linux detected - optimal environment!"
                IS_KALI=true
            else
                log_info "Non-Kali Linux detected ($PRETTY_NAME)"
                log_warning "Some tools may need manual installation"
                IS_KALI=false
            fi
        fi
    else
        log_error "Unsupported operating system: $OSTYPE"
        log_error "This setup script requires Linux (preferably Kali Linux)"
        exit 1
    fi
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 10) else 1)'; then
            log_success "Python $PYTHON_VERSION detected (✓ 3.10+ required)"
        else
            log_error "Python 3.10+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        log_error "Python 3 not found"
        exit 1
    fi
    
    # Check Git
    if command -v git &> /dev/null; then
        log_success "Git found"
    else
        log_error "Git not found - please install git first"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        log_success "pip3 found"
    else
        log_error "pip3 not found - please install python3-pip"
        exit 1
    fi
    
    # Check available disk space (need at least 2GB)
    AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
    REQUIRED_SPACE=2097152  # 2GB in KB
    
    if [ "$AVAILABLE_SPACE" -gt "$REQUIRED_SPACE" ]; then
        log_success "Sufficient disk space available"
    else
        log_warning "Low disk space - may cause issues during installation"
    fi
}

# Install system dependencies
install_system_deps() {
    log_step "Installing system dependencies..."
    
    if [[ "$IS_KALI" == true ]]; then
        # Kali Linux - most tools already available
        log_info "Updating package repository..."
        sudo apt update -qq
        
        log_info "Installing additional packages..."
        sudo apt install -y \
            python3-venv \
            python3-dev \
            build-essential \
            curl \
            wget \
            jq \
            git \
            netcat-traditional \
            nmap \
            masscan \
            gobuster \
            nikto \
            sqlmap \
            dirb \
            netdiscover \
            arp-scan \
            whatweb \
            wpscan \
            nuclei \
            searchsploit \
            metasploit-framework \
            volatility3 \
            binwalk \
            wireshark-common \
            theharvester \
            maltego &> /dev/null || {
            log_warning "Some packages may not be available - continuing anyway"
        }
        
        log_success "Kali Linux dependencies installed"
    else
        # Non-Kali Linux
        log_info "Installing base dependencies for non-Kali system..."
        
        # Detect package manager
        if command -v apt &> /dev/null; then
            sudo apt update -qq
            sudo apt install -y \
                python3-venv \
                python3-dev \
                build-essential \
                curl \
                wget \
                jq \
                git \
                netcat \
                nmap &> /dev/null
        elif command -v yum &> /dev/null; then
            sudo yum install -y \
                python3-devel \
                gcc \
                gcc-c++ \
                make \
                curl \
                wget \
                jq \
                git \
                netcat \
                nmap &> /dev/null
        else
            log_warning "Unknown package manager - some dependencies may be missing"
        fi
        
        log_warning "Non-Kali system detected - you may need to install additional tools manually"
        log_info "Recommended tools: gobuster, nikto, sqlmap, dirb, masscan"
    fi
}

# Install Ollama for LLM support
install_ollama() {
    log_step "Installing Ollama for AI model support..."
    
    if command -v ollama &> /dev/null; then
        log_success "Ollama already installed"
    else
        log_info "Downloading and installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
        
        if command -v ollama &> /dev/null; then
            log_success "Ollama installed successfully"
        else
            log_error "Ollama installation failed"
            return 1
        fi
    fi
    
    # Start Ollama service
    log_info "Starting Ollama service..."
    if systemctl is-active --quiet ollama; then
        log_success "Ollama service is running"
    else
        sudo systemctl start ollama &> /dev/null || {
            log_warning "Could not start Ollama service - you may need to start it manually"
        }
    fi
    
    # Pull required model
    log_info "Downloading AI model (this may take a few minutes)..."
    ollama pull llama3.2 &> /dev/null && {
        log_success "AI model downloaded successfully"
    } || {
        log_warning "Could not download AI model - you can do this later with: ollama pull llama3.2"
    }
}

# Setup Python virtual environment
setup_python_env() {
    log_step "Setting up Python virtual environment..."
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip &> /dev/null
    
    # Install Python dependencies
    log_info "Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt &> /dev/null
        log_success "Python dependencies installed"
    else
        log_warning "requirements.txt not found - installing minimal dependencies"
        pip install fastmcp langchain langgraph rich typer &> /dev/null
    fi
    
    # Install development dependencies if available
    if [ -f "requirements-dev.txt" ]; then
        log_info "Installing development dependencies..."
        pip install -r requirements-dev.txt &> /dev/null
        log_success "Development dependencies installed"
    fi
    
    # Install package in development mode
    log_info "Installing Kali Agents package..."
    pip install -e . &> /dev/null && {
        log_success "Kali Agents package installed"
    } || {
        log_warning "Could not install package in development mode"
    }
}

# Configure environment
configure_environment() {
    log_step "Configuring environment..."
    
    # Copy environment template
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Environment configuration created"
            
            # Auto-detect tool paths and update .env
            log_info "Auto-detecting tool paths..."
            
            tools=("nmap" "gobuster" "sqlmap" "nikto" "dirb" "masscan")
            for tool in "${tools[@]}"; do
                tool_path=$(which $tool 2>/dev/null || echo "")
                if [ ! -z "$tool_path" ]; then
                    # Update .env with found path
                    sed -i "s|${tool^^}_PATH=.*|${tool^^}_PATH=$tool_path|g" .env
                    log_success "Found $tool at $tool_path"
                else
                    log_warning "$tool not found - you may need to install it"
                fi
            done
        else
            log_warning ".env.example not found - creating minimal configuration"
            cat > .env << EOF
# Kali Agents Configuration
LLM_MODEL=llama3.2
LLM_HOST=localhost
LLM_PORT=11434
DEBUG=false
LOG_LEVEL=INFO
EOF
        fi
    else
        log_info "Environment configuration already exists"
    fi
    
    # Create necessary directories
    log_info "Creating necessary directories..."
    mkdir -p logs reports data templates
    log_success "Directories created"
}

# Setup MCP servers
setup_mcp_servers() {
    log_step "Setting up MCP servers..."
    
    # Create MCP server configuration
    if [ ! -f "mcp_config.json" ]; then
        log_info "Creating MCP server configuration..."
        cat > mcp_config.json << EOF
{
    "servers": {
        "network_agent": {
            "command": "python",
            "args": ["-m", "src.mcp_servers.network_server"],
            "env": {}
        },
        "web_agent": {
            "command": "python", 
            "args": ["-m", "src.mcp_servers.web_server"],
            "env": {}
        },
        "vulnerability_agent": {
            "command": "python",
            "args": ["-m", "src.mcp_servers.vuln_server"], 
            "env": {}
        },
        "forensic_agent": {
            "command": "python",
            "args": ["-m", "src.mcp_servers.forensic_server"],
            "env": {}
        },
        "social_agent": {
            "command": "python",
            "args": ["-m", "src.mcp_servers.social_server"],
            "env": {}
        },
        "report_agent": {
            "command": "python",
            "args": ["-m", "src.mcp_servers.report_server"],
            "env": {}
        }
    }
}
EOF
        log_success "MCP server configuration created"
    else
        log_info "MCP server configuration already exists"
    fi
}

# Run system tests
run_tests() {
    log_step "Running system validation tests..."
    
    # Test Python imports
    log_info "Testing Python imports..."
    python3 -c "
try:
    import src
    from src.models import AgentType, Priority
    from src.config.settings import KALI_TOOLS
    print('✅ Core imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
" && log_success "Python imports working" || log_warning "Some imports failed"
    
    # Test Ollama connection
    log_info "Testing Ollama connection..."
    if command -v ollama &> /dev/null; then
        ollama list &> /dev/null && {
            log_success "Ollama connection working"
        } || {
            log_warning "Ollama not responding - may need manual setup"
        }
    fi
    
    # Test CLI command
    log_info "Testing CLI command..."
    if command -v kali-agents &> /dev/null; then
        log_success "CLI command available"
    else
        log_warning "CLI command not found - try: source venv/bin/activate"
    fi
}

# Create desktop shortcuts (optional)
create_shortcuts() {
    log_step "Creating desktop shortcuts..."
    
    if [ -d "$HOME/Desktop" ]; then
        # Demo shortcut
        cat > "$HOME/Desktop/Kali-Agents-Demo.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Kali Agents Demo
Comment=Run Kali Agents demonstration
Exec=bash -c 'cd $(pwd) && source venv/bin/activate && python demo.py; read -p "Press Enter to close..."'
Icon=applications-security
Terminal=true
Categories=Security;System;
EOF
        chmod +x "$HOME/Desktop/Kali-Agents-Demo.desktop"
        
        # CLI shortcut
        cat > "$HOME/Desktop/Kali-Agents-CLI.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Kali Agents CLI
Comment=Open Kali Agents command line interface
Exec=bash -c 'cd $(pwd) && source venv/bin/activate && bash'
Icon=utilities-terminal
Terminal=true
Categories=Security;System;
EOF
        chmod +x "$HOME/Desktop/Kali-Agents-CLI.desktop"
        
        log_success "Desktop shortcuts created"
    else
        log_info "Desktop directory not found - skipping shortcuts"
    fi
}

# Generate usage examples
generate_examples() {
    log_step "Generating usage examples..."
    
    cat > examples.md << 'EOF'
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
EOF
    
    log_success "Usage examples generated in examples.md"
}

# Final system validation
final_validation() {
    log_step "Performing final system validation..."
    
    # Check if virtual environment is working
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        
        # Test basic imports
        python3 -c "
import sys
print(f'Python version: {sys.version}')
try:
    import rich
    print('✅ Rich library available')
    import typer  
    print('✅ Typer library available')
    import fastmcp
    print('✅ FastMCP library available')
    print('✅ All core dependencies working')
except ImportError as e:
    print(f'❌ Dependency error: {e}')
" && log_success "Core dependencies validated" || log_warning "Some dependencies missing"
        
        # Test if demo file is executable
        if [ -f "demo.py" ]; then
            python3 -c "
try:
    import demo
    print('✅ Demo module loadable')
except Exception as e:
    print(f'⚠️  Demo module issue: {e}')
" && log_success "Demo system ready" || log_warning "Demo may have issues"
        fi
        
        # Test CLI if available
        if command -v kali-agents &> /dev/null; then
            kali-agents --help &> /dev/null && {
                log_success "CLI system working"
            } || {
                log_warning "CLI may have issues"
            }
        fi
        
    else
        log_error "Virtual environment not found"
        return 1
    fi
}

# Display completion message
show_completion() {
    echo ""
    echo -e "${GREEN}${CHECKMARK}${CHECKMARK}${CHECKMARK} INSTALLATION COMPLETE! ${CHECKMARK}${CHECKMARK}${CHECKMARK}${NC}"
    echo ""
    echo -e "${CYAN}${ROCKET} Kali Agents is now ready for action! ${ROCKET}${NC}"
    echo ""
    echo -e "${YELLOW}${STAR} Quick Start:${NC}"
    echo -e "  ${BLUE}1.${NC} Activate environment: ${GREEN}source venv/bin/activate${NC}"
    echo -e "  ${BLUE}2.${NC} Run demo:            ${GREEN}python demo.py${NC}"
    echo -e "  ${BLUE}3.${NC} Try CLI:             ${GREEN}kali-agents demo --interactive${NC}"
    echo -e "  ${BLUE}4.${NC} Check status:        ${GREEN}kali-agents status${NC}"
    echo ""
    echo -e "${YELLOW}${STAR} Example Commands:${NC}"
    echo -e "  ${GREEN}kali-agents recon 192.168.1.0/24${NC}"
    echo -e "  ${GREEN}kali-agents web https://target.com${NC}"
    echo -e "  ${GREEN}kali-agents pentest company.com --scope full${NC}"
    echo -e "  ${GREEN}kali-agents osint \"John Doe\" --type person${NC}"
    echo ""
    echo -e "${YELLOW}${STAR} Documentation:${NC}"
    echo -e "  ${BLUE}•${NC} Usage examples: ${GREEN}cat examples.md${NC}"
    echo -e "  ${BLUE}•${NC} Full README:    ${GREEN}cat README.md${NC}"
    echo -e "  ${BLUE}•${NC} Configuration:  ${GREEN}nano .env${NC}"
    echo ""
    echo -e "${PURPLE}${SHIELD} Remember: Always ensure you have proper authorization before testing!${NC}"
    echo -e "${CYAN}${STAR} Kali Agents - 'At Your Service' ${STAR}${NC}"
    echo ""
}

# Error handler
handle_error() {
    log_error "Setup failed at step: $1"
    log_error "Check the error messages above for details"
    log_info "You can try running the setup script again"
    echo ""
    echo -e "${YELLOW}Common solutions:${NC}"
    echo -e "  ${BLUE}•${NC} Ensure you have internet connection"
    echo -e "  ${BLUE}•${NC} Check if you have sufficient permissions"  
    echo -e "  ${BLUE}•${NC} Install missing system dependencies manually"
    echo -e "  ${BLUE}•${NC} Try running: ${GREEN}sudo apt update && sudo apt upgrade${NC}"
    exit 1
}

# Main installation function
main() {
    print_banner
    
    echo -e "${CYAN}${ROCKET} Starting Kali Agents MCP installation...${NC}"
    echo -e "${YELLOW}This will set up the complete intelligent cybersecurity automation system${NC}"
    echo ""
    
    # Confirm installation
    read -p "Continue with installation? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        log_info "Installation cancelled by user"
        exit 0
    fi
    
    # Run installation steps
    check_root || handle_error "root check"
    check_requirements || handle_error "requirements check"
    install_system_deps || handle_error "system dependencies"
    install_ollama || handle_error "ollama installation"
    setup_python_env || handle_error "python environment"
    configure_environment || handle_error "environment configuration"
    setup_mcp_servers || handle_error "MCP server setup"
    create_shortcuts || handle_error "desktop shortcuts"
    generate_examples || handle_error "example generation"
    run_tests || handle_error "system tests"
    final_validation || handle_error "final validation"
    
    show_completion
}

# Cleanup function for interruption
cleanup() {
    echo ""
    log_warning "Installation interrupted by user"
    log_info "Partial installation may be present"
    log_info "You can run the setup script again to continue"
    exit 1
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
