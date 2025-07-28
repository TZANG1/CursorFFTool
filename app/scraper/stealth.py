"""
Stealth module for avoiding bot detection
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import time
from typing import Optional
from loguru import logger

class StealthConfig:
    """Configuration for stealth browsing"""
    
    # Realistic user agents
    USER_AGENTS = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
    
    # Common screen resolutions
    RESOLUTIONS = [
        (1920, 1080),
        (1366, 768),
        (1536, 864),
        (1440, 900),
        (1280, 720)
    ]
    
    # Realistic typing speeds (characters per minute)
    MIN_TYPING_SPEED = 200
    MAX_TYPING_SPEED = 500
    
    # Mouse movement parameters
    MOUSE_MOVE_MIN_POINTS = 10
    MOUSE_MOVE_MAX_POINTS = 20
    
    # Viewport sizes
    VIEWPORT_SIZES = [
        {'width': 1280, 'height': 800},
        {'width': 1440, 'height': 900},
        {'width': 1920, 'height': 1080}
    ]

def create_stealth_driver() -> Optional[webdriver.Chrome]:
    """Create a new Chrome driver with stealth settings"""
    try:
        options = Options()
        
        # Random user agent
        user_agent = random.choice(StealthConfig.USER_AGENTS)
        options.add_argument(f'--user-agent={user_agent}')
        
        # Random viewport size
        viewport = random.choice(StealthConfig.VIEWPORT_SIZES)
        options.add_argument(f'--window-size={viewport["width"]},{viewport["height"]}')
        
        # Essential anti-bot options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Additional stealth options
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--lang=en-US,en;q=0.9')
        
        # Create driver
        driver = webdriver.Chrome(options=options)
        
        # Execute stealth scripts
        _inject_stealth_scripts(driver)
        
        # Set random resolution
        resolution = random.choice(StealthConfig.RESOLUTIONS)
        driver.set_window_size(resolution[0], resolution[1])
        
        return driver
        
    except Exception as e:
        logger.error(f"Failed to create stealth driver: {e}")
        return None

def _inject_stealth_scripts(driver: webdriver.Chrome):
    """Inject scripts to avoid detection"""
    try:
        # Override navigator.webdriver
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })
        
        # Add realistic navigator properties
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            "source": """
                const newProto = navigator.__proto__;
                delete newProto.webdriver;
                navigator.__proto__ = newProto;
                
                // Add plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {
                            0: {type: "application/x-google-chrome-pdf"},
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        }
                    ]
                });
                
                // Add languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ["en-US", "en"]
                });
            """
        })
        
        # Override permissions
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            "source": """
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """
        })
        
    except Exception as e:
        logger.warning(f"Failed to inject some stealth scripts: {e}")

def human_like_typing(element, text: str):
    """Simulate human-like typing"""
    for char in text:
        element.send_keys(char)
        # Random delay between keystrokes
        time.sleep(random.uniform(
            60/StealthConfig.MAX_TYPING_SPEED,
            60/StealthConfig.MIN_TYPING_SPEED
        ))

def random_scroll(driver: webdriver.Chrome, scroll_amount: int):
    """Perform random, human-like scrolling"""
    current = 0
    while current < scroll_amount:
        # Random scroll step between 100 and 300 pixels
        step = random.randint(100, 300)
        current += step
        
        # Occasionally scroll back up slightly
        if random.random() < 0.2:  # 20% chance
            current -= random.randint(30, 70)
        
        driver.execute_script(f"window.scrollTo(0, {current});")
        
        # Random pause between scrolls
        time.sleep(random.uniform(0.5, 2.0))

def add_random_delays():
    """Generate random delay time for actions"""
    return random.uniform(2, 5)

def simulate_human_behavior(driver: webdriver.Chrome):
    """Simulate random human-like behavior"""
    try:
        # Random mouse movements
        driver.execute_script("""
            function generatePoints(numPoints) {
                const points = [];
                for (let i = 0; i < numPoints; i++) {
                    points.push({
                        x: Math.random() * window.innerWidth,
                        y: Math.random() * window.innerHeight
                    });
                }
                return points;
            }
            
            const points = generatePoints(Math.floor(Math.random() * 10) + 5);
            points.forEach((point, i) => {
                setTimeout(() => {
                    const event = new MouseEvent('mousemove', {
                        view: window,
                        bubbles: true,
                        cancelable: true,
                        clientX: point.x,
                        clientY: point.y
                    });
                    document.dispatchEvent(event);
                }, i * (Math.random() * 200 + 100));
            });
        """)
        
        # Random viewport changes
        if random.random() < 0.3:  # 30% chance
            viewport = random.choice(StealthConfig.VIEWPORT_SIZES)
            driver.set_window_size(viewport['width'], viewport['height'])
        
        # Random page interactions
        driver.execute_script("""
            function randomInteraction() {
                const elements = document.querySelectorAll('a, button, input');
                elements.forEach(el => {
                    if (Math.random() < 0.1) {  // 10% chance for each element
                        el.addEventListener('mouseover', () => {});
                    }
                });
            }
            randomInteraction();
        """)
        
    except Exception as e:
        logger.warning(f"Failed to simulate some human behaviors: {e}") 