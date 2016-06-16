if __name__=="__main__":
    import pickle
    import simulate
    import cProfile

    p = pickle.load(open("longtest.p","r"))
    G = p.species.getAllGenomes()[37]

    pr =cProfile.Profile()
    pr.enable()
    G.mutate(p.innovations)
    pr.print_stats()