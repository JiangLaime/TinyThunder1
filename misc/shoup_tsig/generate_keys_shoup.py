from shoup import *
import argparse
import pickle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('players', help='The number of players')
    parser.add_argument('k', help='k')
    args = parser.parse_args()
    players = int(args.players)
    k = int(args.k)
    PK, SKs = dealer(players=players, k=k)
    print (pickle.dumps((PK, SKs)))

if __name__ == '__main__':
    main()
    