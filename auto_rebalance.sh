#!/bin/sh

echo "STARTING REBALANCE @ `date`"

echo "Starting bitstamp -> nicehash rebalance"
# bitstamp -> nicehash
python3 home/peter/python/src/rebalance-lnd/rebalance.py -f 710251526247022593 -t 709644595846447105 -a 1000000
python3 home/peter/python/src/rebalance-lnd/rebalance.py -f 710251526247022593 -t 709644595846447105 -a 500000
python3 home/peter/python/src/rebalance-lnd/rebalance.py -f 710251526247022593 -t 709644595846447105 -a 200000

echo "Starting bitstamp -> hodlister_co rebalance"
# bitstamp -> hodlister_co
python3 home/peter/python/src/rebalance-lnd/rebalance.py -f 710251526247022593 -t 710335089135648768 -a 1000000
python3 home/peter/python/src/rebalance-lnd/rebalance.py -f 710251526247022593 -t 710335089135648768 -a 500000
python3 home/peter/python/src/rebalance-lnd/rebalance.py -f 710251526247022593 -t 710335089135648768 -a 200000

echo "Starting bitstamp -> CoinGate rebalance"
# bitstamp -> CoinGate
python3 home/peter/python/src/rebalance-lnd/rebalance.py -f 710251526247022593 -t 711522561697579008 -a 1000000
python3 home/peter/python/src/rebalance-lnd/rebalance.py -f 710251526247022593 -t 711522561697579008 -a 500000
python3 home/peter/python/src/rebalance-lnd/rebalance.py -f 710251526247022593 -t 711522561697579008 -a 200000

echo "Starting bitstamp -> lnamrkets rebalance"
# bitstamp -> lnmarkets
python3 home/peter/python/src/rebalance-lnd/rebalance.py -f 710251526247022593 -t 709650093463896064 -a 1000000
python3 home/peter/python/src/rebalance-lnd/rebalance.py -f 710251526247022593 -t 709650093463896064 -a 500000
python3 home/peter/python/src/rebalance-lnd/rebalance.py -f 710251526247022593 -t 709650093463896064 -a 200000

echo "--------------------------------------- END REBALANCE @ `date` -------------------------------------------"