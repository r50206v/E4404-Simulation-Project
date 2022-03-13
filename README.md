# E4404-Simulation-Project
Simulation Project: Inventory Memanagement and Dynamic Pricing Strategy

### Project Goals:
1. Client wants to know how the hurricane would influence its profit by analyzing its frequency and scale(1,2,3,4,5);
2. Client wants to see how the daily orange juice price change would be next year according to history data;
3. Client wants us to simulate its customer arrivals in order to visualize their daily demands;
4. Ultimately, client wants to get some useful insights on how to optimize its profit

### Background Settings:
1. Dataset - Florida Hurricane Historical Data, Orange Juice Future Price (FCOJ-A Futures)
2. Product - Orange
3. Location - Florida

### Simulation Settings: 
1. Client run a local orange firm Orange in Miami, where they manufacture and sell orange juice at the price of FCOJ-A Futures;
2. The customers of the orange firm are mainly local fruit stores, fresh markets, and wholefood markets, and their daily arrivals follow non homogeneous poisson process;
3. Both of the future price and demand (customer arrival) would be subject to hurricane in southeast US, which has seasonality and periodicity, thus needs to be considered when making supply management decisions

### Package Installation:
```pip install -r requirements.txt```