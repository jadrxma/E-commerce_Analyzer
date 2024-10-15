import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import time
import math
from concurrent.futures import ThreadPoolExecutor

# Function to detect Shopify
def detect_shopify(soup, headers):
    if soup.find("script", src=lambda x: x and 'shopify' in x) or 'X-ShopId' in headers:
        return "Shopify"
    return None

# Function to detect WooCommerce
def detect_woocommerce(soup):
    if soup.find("meta", {"name": "generator", "content": lambda x: x and 'WooCommerce' in x}):
        return "WooCommerce"
    return None

# Function to detect Magento
def detect_magento(soup):
    if soup.find("script", src=lambda x: x and 'mage' in x) or soup.find("link", href=lambda x: x and 'Magento' in x):
        return "Magento"
    return None

# Function to detect BigCommerce
def detect_bigcommerce(soup):
    if soup.find("script", src=lambda x: x and 'bigcommerce' in x):
        return "BigCommerce"
    return None

# Function to detect Northbeam in the <head> section
def detect_northbeam_in_head(soup):
    head = soup.find('head')
    if head:
        scripts = head.find_all('script')
        for script in scripts:
            if script.get('src') and 'northbeam' in script.get('src'):
                return "Northbeam"
            if script.string and 'northbeam' in script.string.lower():
                return "Northbeam"
    return None

# Function to detect e-commerce platforms for a single URL with timeout
def detect_platforms(url):
    try:
        response = requests.get(url, timeout=10)  # Set timeout to 10 seconds
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            headers = response.headers
            
            results = {}
            
            shopify = detect_shopify(soup, headers)
            woocommerce = detect_woocommerce(soup)
            magento = detect_magento(soup)
            bigcommerce = detect_bigcommerce(soup)
            northbeam = detect_northbeam_in_head(soup)
            
            if shopify:
                results['E-commerce Platforms'] = shopify
            if woocommerce:
                results['E-commerce Platforms'] = woocommerce
            if magento:
                results['E-commerce Platforms'] = magento
            if bigcommerce:
                results['E-commerce Platforms'] = bigcommerce
            if northbeam:
                results['E-commerce Platforms'] = northbeam

            return results if results else {"E-commerce Platforms": "Unknown platform"}
        else:
            return {"E-commerce Platforms": "Error retrieving content"}
    
    except requests.exceptions.Timeout:
        return {"E-commerce Platforms": "Timeout, skipped"}
    except Exception as e:
        return {"E-commerce Platforms": f"Error occurred: {e}"}

# Streamlit app layout
st.title("E-commerce Platform Detector")

# Upload CSV file
uploaded_file = st.file_uploader("Choose a CSV file with websites", type="csv")

if uploaded_file is not None:
    # Read CSV file
    df = pd.read_csv(uploaded_file)
    
    # Check if 'website' column exists
    if 'website' not in df.columns:
        st.error("CSV file must contain a 'website' column.")
    else:
        # Initialize the Detected Platforms column
        df['Detected Platforms'] = None

        # Split the websites into batches of 100
        batch_size = 100
        total_batches = math.ceil(len(df) / batch_size)
        
        # Iterate through batches
        for batch_num in range(total_batches):
            start_row = batch_num * batch_size
            end_row = min((batch_num + 1) * batch_size, len(df))
            batch_df = df.iloc[start_row:end_row].copy()  # Make a deep copy to avoid the warning
            
            st.write(f"Processing batch {batch_num + 1} of {total_batches}")
            
            # Progress bar for the batch
            batch_progress_bar = st.progress(0)
            
            # Concurrency for batch processing
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for index, website in enumerate(batch_df['website']):
                    futures.append(executor.submit(detect_platforms, website))
                
                for i, future in enumerate(futures):
                    result = future.result()
                    
                    # Update the original DataFrame df, not the slice
                    df.loc[start_row + i, 'Detected Platforms'] = result.get('E-commerce Platforms')
                    
                    # Update batch progress bar
                    batch_progress_bar.progress((i + 1) / batch_size)

            # Reflect the changes in batch_df by reassigning values from df
            batch_df['Detected Platforms'] = df.loc[start_row:end_row, 'Detected Platforms']

            # Print the results for this batch
            st.write(f"Results for batch {batch_num + 1}")
            st.write(batch_df[['website', 'Detected Platforms']])
            
            # Save each batch as a separate downloadable CSV
            csv_chunk = batch_df.to_csv(index=False)
            st.download_button(
                label=f"Download batch {batch_num + 1} as CSV",
                data=csv_chunk,
                file_name=f'platform_results_batch_{batch_num + 1}.csv',
                mime='text/csv',
            )

        # Optionally, display all results
        st.write(df)
