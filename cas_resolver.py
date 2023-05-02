import cirpy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pubchempy import get_cids

def get_cas_from_name(substance_name, method = 'pubchem',driver = None, first_only = True,  verbose = False,):
    """Function to retrieve the CAS identifer from the name of a molecule
    Two methods are available : 
    cirpy: uses the Chemical Identifier Resolver (CIR) : this method is fast but fails often
    pubchem: uses the pubchem database to webscrapp the url : slower but more robust
    
    Args:
        name (str): The name of the molecule to resolve
        method (str): The method to use. It can be 'pubchem' or 'cirpy' (not recommended)
        driver (Selenium Webdriver) : The web driver to load the pubchem pages. If not provided the driver will be
            instanciated for each call of the function
        first_only (bool): Wether to return only the first CAS retrieved by the methods (default True)
        verbose (bool) : The level of verbosity

    Returns:
        cas (str): The resolved cas identifier if first_only=True
        cas_list (list) : The resolved cas identifiers if first_only=False """
    if verbose :
        print(f'Resolving the name {substance_name} using {method}')

    if method == 'cirpy':
        try:
            cas_list =  cirpy.resolve(substance_name, 'cas')
        except:
           print('Substance not found in CIR')
           return
        
    elif method == 'pubchem':
        #If driver is not provided, initialize it
        if driver is None :
            driver = webdriver.Chrome()
        # First get the CID (pubchemID) of the substance
        try:
            CID = get_cids(substance_name, 'name')[0] #Only keep best match
        except:
            print('Substance not found in PubChem')
            return
        if verbose:
            print(f'Top matching CID : {CID}')
        #Load the corresponding pubchem page with the CID
        url = f"https://pubchem.ncbi.nlm.nih.gov/compound/{CID}#section=CAS"
        driver.get(url)
        #Xpath of the CAS
        x_path = "//*[@id='CAS']/div[@class='section-content']/div[@class='section-content-item']/p"
        # Wait for the page to load our element of interest
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.visibility_of_element_located((By.XPATH, x_path)))
        except:
            print('No CAS found in the webpage after 10 sec of loading')
            return
        #Find the correct web elements
        elements = driver.find_elements(By.XPATH,x_path )         
        #Extract the CAS identifiers
        cas_list = []
        for i in range(len(elements)):
            cas_list.append(elements[i].text)

    #Close the driver
    if driver is None:
        driver.close()       

    if first_only:
        return cas_list[0]
    else:
        return cas_list