# Dukascopy data downloader

Finding good Forex data is difficult and expensive. Dukascopy has made available an excellent web tool  https://www.dukascopy.com/swiss/english/marketwatch/historical/ to download tick data for a large a variaty of Forex, CFD and commodities. This is awesome and extremely useful. However, it would take a lot of time to download a large data set from the website. In order to solve this issue, I created `duka`. `duka` is a small terminal application which download ticks data from the Dukascopy historical repo and saves it in the csv format.  


## Installation

`duka` requires python 3.5 and aiohttp 0.21.5. It can be installed using `pip` as follows:

```
pip install duka
```

## Usage

- Help :
```
duka -h
```
- Download last available data set (i.e. yestarday if not Saturday ) for EURUSD and GBPUSD
```
 duka EURUSD GBPUSD 
```
- Download ticks for the EURUSD for a specific day
``` 
duka EURUSD -d 2016-02-02
```
- Download ticks for the EURUSD for a given period. For example this download all ticks for the 2015 year
```
duka EURUSD -s 2015-01-01 -e 2016-12-31 
```
- Download ticks for N currency until now. The following command dowloads all ticks for GBPUSD and EURUSD since the beginning of 2016
```
duka EURUSD -s 2016-01-01
```



