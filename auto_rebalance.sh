#!/bin/sh

echo "STARTING REBALANCE @ `date`"

echo "Starting bitstamp -> nicehash rebalance"
# bitstamp -> nicehash
python3 /home/peter/python/src/rebalance-lnd/rebalance.py -f 715522585012404225 -t 709644595846447105 -a 400000 -l 3 --max-fee-factor 60

echo "Starting bitstamp -> hodlister_co rebalance"
# bitstamp -> hodlister_co
python3 /home/peter/python/src/rebalance-lnd/rebalance.py -f 715522585012404225 -t 710335089135648768 -a 400000 -l 3 --max-fee-factor 60

echo "Starting bitstamp -> CoinGate rebalance"
# bitstamp -> CoinGate
python3 /home/peter/python/src/rebalance-lnd/rebalance.py -f 715522585012404225 -t 711522561697579008 -a 400000 -l 3 --max-fee-factor 60

echo "Starting bitstamp -> lnamrkets rebalance"
# bitstamp -> lnmarkets
python3 /home/peter/python/src/rebalance-lnd/rebalance.py -f 715522585012404225 -t 709650093463896064 -a 400000 -l 3 --max-fee-factor 60

echo "Starting bitstamp -> walet of satoshi rebalance"
# bitstamp -> walet of satoshi
python3 /home/peter/python/src/rebalance-lnd/rebalance.py -f 715522585012404225 -t 711575338232512512 -a 400000 -l 3 --max-fee-factor 60

echo "Starting bitstamp -> citadel21 rebalance"
# bitstamp -> citadel21
python3 /home/peter/python/src/rebalance-lnd/rebalance.py -f 715522585012404225 -t 706717695977979905 -a 200000 -l 3 --max-fee-factor 30

echo "Starting bitstamp -> rompert rebalance"
# bitstamp -> rompert
python3 /home/peter/python/src/rebalance-lnd/rebalance.py -f 715522585012404225 -t 709139920050323456 -a 100000 -l 2 --max-fee-factor 15

echo "Starting bitstamp -> ion.radar.tech rebalance"
# bitstamp -> ion.radar.tech
python3 /home/peter/python/src/rebalance-lnd/rebalance.py -f 715522585012404225 -t 710299904768933889 -a 400000 -l 3 --max-fee-factor 60

echo "Starting bitstamp -> TYLERDURDEN rebalance"
# bitstamp -> TYLERDURDEN
python3 /home/peter/python/src/rebalance-lnd/rebalance.py -f 715522585012404225 -t 702520859994226689 -a 400000 -l 3 --max-fee-factor 60

echo "Starting bitstamp -> ACINQ rebalance"
# bitstamp -> ACINQ
python3 /home/peter/python/src/rebalance-lnd/rebalance.py -f 715522585012404225 -t 714957436098445312 -a 400000 -l 3 --max-fee-factor 60


echo "--------------------------------------- END REBALANCE @ `date` -------------------------------------------"