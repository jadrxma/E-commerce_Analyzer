import requests
from bs4 import BeautifulSoup
import streamlit as st

# Function to detect Shopify
def detect_shopify(soup, headers):
    if soup.find("script", src=lambda x: x and 'shopify' in x) or 'X-ShopId' in headers:
        print("Detected Shopify")  # Debug print
        return True
    return False

# Function to detect WooCommerce
def detect_woocommerce(soup):
    if soup.find("meta", {"name": "generator", "content": lambda x: x and 'WooCommerce' in x}):
        print("Detected WooCommerce")  # Debug print
        return True
    return False

# Function to detect Magento
def detect_magento(soup):
    if soup.find("script", src=lambda x: x and 'mage' in x) or soup.find("link", href=lambda x: x and 'Magento' in x):
        print("Detected Magento")  # Debug print
        return True
    return False

# Function to detect BigCommerce
def detect_bigcommerce(soup):
    if soup.find("script", src=lambda x: x and 'bigcommerce' in x):
        print("Detected BigCommerce")  # Debug print
        return True
    return False

# Function to detect Northbeam in the <head> section and print the <head>
def detect_northbeam_in_head(soup):
    head = soup.find('head')
    if head:
        # Print the full content of the <head> section
        print(f"<head> Content: {head.prettify()}")  # Debug print to show the entire <head> section
        # Search within all script tags in the <head>
        scripts = head.find_all('script')
        for script in scripts:
            # Check both src attribute and script content
            if script.get('src') and 'northbeam' in script.get('src'):
                print(f"Detected Northbeam in script src: {script.get('src')}")  # Debug print if found in src
                return True
            if script.string and 'northbeam' in script.string.lower():
                print(f"Detected Northbeam in inline script: {script.string[:100]}...")  # Debug print if found in inline script
                return True
    return False

# Function to check if the website uses an e-commerce platform or Northbeam
def detect_ecommerce_platforms(url):
    try:
        # Send a request to the website
        response = requests.get(url)
        print(f"Fetching URL: {url} - Status Code: {response.status_code}")  # Debug print
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            headers = response.headers
            
            # List to accumulate detected platforms
            platforms = []
            
            # Detect various e-commerce platforms
            if detect_shopify(soup, headers):
                platforms.append("Shopify")
            if detect_woocommerce(soup):
                platforms.append("WooCommerce")
            if detect_magento(soup):
                platforms.append("Magento")
            if detect_bigcommerce(soup):
                platforms.append("BigCommerce")
            if detect_northbeam_in_head(soup):
                platforms.append("Northbeam")
            
            # Print detected platforms for debugging
            print(f"Detected platforms: {platforms}")  # Debug print
            
            # Return all detected platforms, or notify if none detected
            if platforms:
                return ", ".join(platforms)  # Return platforms as a comma-separated string
            else:
                return "Unknown platform or not detected."
        else:
            return "Error: Unable to retrieve website content."
    
    except Exception as e:
        print(f"Error occurred: {e}")  # Debug print
        return f"Error occurred: {e}"

# Streamlit app layout
st.title("E-commerce & Analytics Platform Detector")

# Input for the website URL
url = st.text_input("Enter website URL (include https:// or http://):", "")

# Button to check if the website is using an e-commerce platform or Northbeam
if st.button("Check"):
    if url:
        platforms = detect_ecommerce_platforms(url)
        print(f"Final output: {platforms}")  # Debug print
        if "Error" in platforms:
            st.error(platforms)
        elif platforms == "Unknown platform or not detected.":
            st.warning(f"❌ {url} does not seem to use a detectable platform.")
        else:
            st.success(f"✅ {url} is using: {platforms}")
    else:
        st.error("Please enter a valid URL.")
