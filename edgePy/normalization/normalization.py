# Should really read something like
# def cpm(DGEList):
#   return (DGEList.counts / np.sum(DGEList.counts, axis=0) * 1000000)

# @Michael why not:
#   DGEList().cpm()
def cpm(countsArray):

    return (countsArray / np.sum(countsArray, axis=0)) * 1000000


def logcpm(countsArray, prior_count=0.25):
    

    cpm = (countsArray / np.sum(countsArray, axis=0)) * 1000000

    cpm[cpm == 0] = prior_count

    return np.log(cpm)


#def tpm(DGEList):
#   DGEList.counts / len(DGEList.genes[i]) (or whatever)

def tpm(DGEList):

    pass
