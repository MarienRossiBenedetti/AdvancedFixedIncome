# -------- SOME USEFULL FUNCTIONS FOR FIXED INCOME & CREDIT COURSE --------

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def zc_bond(N, T, r, simple_rate=True):
    """
    Computes the price of a Zero-Coupon Bond (discount factor)
    N : Face Value of the Bond
    T : Maturity of the Bond
    r : Discounted Rate
    """
    return N/(1+r*T)

def simple_to_comp(simple_rate, t, freq_per_year):
    """
    Returns the compounded rate from the simple rate 
    """
    return ((1+simple_rate*t)**(1/(t*freq_per_year))-1)*freq_per_year
    
def comp_to_simple(comp_rate, t, freq_per_year):
    """
    Returns the simple rate from the compounded rate 
    """
    return ((1+comp_rate/freq_per_year)**(t*freq_per_year)-1)/t

def pv_simple(cf, r, tau):
    """
    Compute the PV of a future cash flow cf discounted back at the simple rate r
    """
    return np.round(zc_bond(N=1, T=tau, r=r, simple_rate=True)*cf, 4)

def bond_s_price(N, cpn_ann, T, freq_per_year, zc_rates: pd.Series):
    """
    Computes the price of a Bond 
    N             : Face Value of the Bond
    cpn_ann       : Annual Coupon Rate of the Bond
    T             : Maturity
    freq_per_year : Frequency of the Coupon Payments per Year
    zc_rates      : Series of ZC Rates    
    """
    # Extract each CFs 
    nbre_payments = int(T*freq_per_year)
    CFs = pd.Series([cpn_ann*N*(1/freq_per_year) for i in range(nbre_payments)])
    # Add the Face Value to the last Coupon Payment
    CFs.iloc[-1] += N 
    # Extract Zero Coupon Bonds Prices (discount factors)
    zc_prices = pd.Series([zc_bond(N=1, T=(i+1)*(1/freq_per_year), r=zc_rates.iloc[i], simple_rate=True) for i in range(nbre_payments)])
    # Discount Back and Sum the PVs of each CF
    return np.round((CFs * zc_prices).sum(), 4)

def create_bond(N, T, cpn_ann, freq_per_year):
    """
    Creates a Bond that will be contained into a DataFrame
    """
    bond = pd.Series({"Nominal"            : N,
                      "Tenor (Years)"      : T,
                      "Annual Coupon"      : cpn_ann,
                      "Payments Frequency" : freq_per_year
                     })
    return bond

def bond_c_price(bond, yc):
    """
    Computes the Price of a Bond with Compounded Returns as input
    """
    N = bond["Nominal"]
    T = bond["Tenor (Years)"]
    cpn_ann = bond["Annual Coupon"]
    freq = bond["Payments Frequency"]
    
    # Extract each CFs 
    nbre_payments = int(T*freq)
    CFs = pd.Series([cpn_ann*N*(1/freq) for i in range(nbre_payments)])
    # Add the Face Value to the last Coupon Payment
    CFs.iloc[-1] += N 
    
    # Timeline of Payments
    tl = pd.Series([(i+1)*(1/freq) for i in range(nbre_payments)])

    return (CFs/((1+yc/freq)**(tl*freq))).sum()
    
def macaulay_duration(bond, yc):
    """
    Computes the Macaulay Duration of a Bond (Sensitivity to Interest Rates)
    yc   : Compounded Yield
    bond : Series DataFrame returned by the function create_bond
    """
    N = bond["Nominal"]
    T = bond["Tenor (Years)"]
    cpn_ann = bond["Annual Coupon"]
    freq = bond["Payments Frequency"]
    
    # Extract each CFs 
    nbre_payments = int(T*freq)
    CFs = pd.Series([cpn_ann*N*(1/freq) for i in range(nbre_payments)])
    # Add the Face Value to the last Coupon Payment
    CFs.iloc[-1] += N 
    
    # Timeline of Payments
    tl = pd.Series([(i+1)*(1/freq) for i in range(nbre_payments)])
    
    # Decomposition of Mac Duration
    num = tl*np.exp(-yc*tl)*CFs
    den = bond_c_price(bond, yc=yc)
    
    return np.round((num/den).sum(), 4)

def modified_macaulay_duration(bond, yc):
    """
    Computes the Modified Macaulay Duaration of a Bond
    bond : Series DataFrame as returned by the function create_bond
    yc   : Compounded Yield
    """
    freq = bond["Payments Frequency"]
    
    return np.round(macaulay_duration(bond, yc)/(1+(yc/freq)), 4)

def bond_stats(bond, yc):
    """
    Returns a DataFrame with the stats of the Bond
    bond : Series DataFrame as returned by the function create_bond
    yc   : Compounded Yield
    """
    stats = pd.Series({"Price" : bond_c_price(bond, yc),
                       "Macaulay Duration" : macaulay_duration(bond, yc),
                       "Modified Macaulay" : modified_macaulay_duration(bond, yc)
                       })
    
    return stats