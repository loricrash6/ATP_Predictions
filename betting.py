class Bets:
    def __init__(self, method):
        self.method = method


    def bet(self, predictions, odds_p1, odds_p2):
        """
        To evaluate, we bet a fix amount
        Three streategies are implemented
        Output: bets :array of {-1,+1,0}: -1 if we bet on p1, +1 for a bet on p2 and 0 if no bet
                amount: array with the amount placed on each bet (between 0 and 1)
        """
        bets=[]
        if self.method=='simple':
            #bet on predicted winner
            bets, amounts = [-1 if prediction>0.5 else +1 for prediction in predictions], [1]*len(predictions)
        
        if self.method=='better_odds':
            #bet a fixed amount when predicted probability of a player winning a match is higher than implied probability
            #implied_probs_p1=[odds_p1[i]/(odds_p1[i]+odds_p2[i]) for i in range(len(predictions))]
            implied_probs_p1=[ 1/odds_p1[i] for i in range(len(predictions))]
            #implied_probs_p2=[odds_p2[i]/(odds_p1[i]+odds_p2[i]) for i in range(len(predictions))]
            implied_probs_p2=[ 1/odds_p2[i] for i in range(len(predictions))]
            
            #BETS: ADDED prediction>0.5! Don't wanna bet on players who'll almost surely lose!
            bets=[-1 if predictions[i]>implied_probs_p1[i] and predictions[i]>0.3 else +1 if 1-predictions[i]>implied_probs_p2[i] and predictions[i]<0.7 else 0 for i in range(len(predictions))]
            amounts=[0 if bet==0 else 1 for bet in bets]


        if self.method=='kelly':
            #bet a fraction
            #implied_probs_p1=[odds_p2[i]/(odds_p1[i]+odds_p2[i]) for i in range(len(predictions))]
            #implied_probs_p2=[odds_p1[i]/(odds_p1[i]+odds_p2[i]) for i in range(len(predictions))]
            implied_probs_p1=[ 1/odds_p1[i] for i in range(len(predictions))]
            implied_probs_p2=[ 1/odds_p2[i] for i in range(len(predictions))]
            bets=[-1 if predictions[i]>implied_probs_p1[i] else +1 if (1-predictions[i])>implied_probs_p2[i] else 0 for i in range(len(predictions))]
            #bets = [-1 if predictions[i] - (1-predictions[i])/(odds_p1[i]-1) > 0 else +1 if 1-predictions[i] - predictions[i]/(odds_p2[i]-1) > 0 else 0 \
            #for i in range(len(predictions))]
            #print(bets)
            #amounts = [ 0 if bets[i]==0 else (predictions[i]*(odds_p1[i])-1)/(odds_p1[i]-1) if bets[i]==-1 else \
            #((1-predictions[i])*(odds_p2[i])-1)/(odds_p2[i]-1) for i in range(len(predictions)) ]
            amounts = [round(predictions[i] - (1-predictions[i])/(odds_p1[i]-1),2) if bets[i]==-1 else round(1-predictions[i] - \
                predictions[i]/(odds_p2[i]-1),2) if bets[i]==+1 else 0 for i in range(len(predictions))]

        #print(f'Bets {sum(amounts)} over {sum([1 if amount>0 else 0 for amount in amounts])} games, out of {len(predictions)}')
        print('\tBets {}€ over {} games, out of {}'.format(round(sum(amounts),2),sum([1 if amount>0 else 0 for amount in amounts]),len(predictions)))  
        return bets, amounts
    
    def roi(self, predictions, odds_p1, odds_p2, winners):
        "winners: array 0 if p1, 1 if p2"
        bets, amounts = self.bet(predictions,odds_p1, odds_p2)

        #amounts=[x if x>=0 else 0 for x in amounts ]
        #print(amounts)

        #gains=[0]*len(bets)
        gains=[]
        

        #nb_won = 0
        
        for i in range(len(bets)):

            if (bets[i]==(-1) and winners[i]==0):
                #gains[i] = odds_p1[i]*amounts[i]
                gains.append(odds_p1[i]*amounts[i])
        

            if (bets[i]==1 and winners[i]==1): 
                #gains[i] = odds_p2[i]*amounts[i]
                gains.append(odds_p2[i]*amounts[i])

            else:
                #gains[i] = 0
                gains.append(0)

        """
        gains = [odds_p1[i]*amounts[i] if (bets[i]==-1 and winners[i]==0) else odds_p2[i]*amounts[i] if (bets[i]==1 and winners[i]==1) else 0 \
        for i in range(len(bets))]
        print(gains)
        """
        nb_won = sum([1 if (((bets[i]==-1 and winners[i]==0) or (bets[i]==1 and winners[i]==1)) and amounts[i]>0) else 0 for i in range(len(bets))])
        nb_lost = sum([0 if (((bets[i]==-1 and winners[i]==0) or (bets[i]==1 and winners[i]==1)) and amounts[i]>0) else 1 if amounts[i]>0 else 0 for i in range(len(bets))])

        print('\t{} winned bets and {} lost bets, gains of {}€ investing {}€'.format(nb_won,nb_lost,round(sum(gains),2),round(sum(amounts),2)))
        
        return (sum(gains)-sum(amounts))/sum(amounts)

def kelly_bet(bets):
    # KELLY CRITERION BETTING MODIFIED!
    #print(bets.loc[0,:])
    x=range(bets.shape[0])
    y=[]
    budget=100
    b=0 #amount placed on bets
    r=0 #return
    q=1 #max bet size
    n_bets=[0,0,0] #placed, won, lost
    #print("Starting with: {}€".format(b))
    #print("\n...betting ongoing with Kelly criterion...\n")
    for i in range(bets.shape[0]):

        #print(bets.loc[i,:])

        #print("\n Currently betting on {} vs {}:\n\t- ML estimated probabilites: {} vs {}\n\t- B365 odds: {} vs {}".\
        #   format(bets.loc[i,"p0"],bets.loc[i,"p1"],bets.loc[i,"prob0"],bets.loc[i,"prob1"],bets.loc[i,"odd0"],bets.loc[i,"odd1"]))

        #evaluate implied probabilities from odds
        p0_ip=1/bets.loc[i,"odd0"]
        p1_ip=1/bets.loc[i,"odd1"]

        #print("P_bookies - player 0 to win: {}, player 1 to win: {}".format(p0_ip,p1_ip))

        s0=0
        if bets.loc[i,"prob0"]>(p0_ip) and bets.loc[i,"prob0"]>0.3: 
            #s0=float(round(q*((bets.loc[i,"prob0"]*bets.loc[i,"odd0"]-1)/(bets.loc[i,"odd0"]-1)),2))
            s0=1
            #print("Betting {} on player 0".format(s0))
        
        s1=0
        if bets.loc[i,"prob1"]>(p1_ip) and bets.loc[i,"prob1"]>0.3:
            s1=1
            #s1=float(round(q*((bets.loc[i,"prob1"]*bets.loc[i,"odd1"]-1)/(bets.loc[i,"odd1"]-1)),2))
            #print("Betting {} on player 1".format(s1))
            
        if s0<=0:
            s0=0
        #elif s0>0 and s0<2: #min quota: 2€
        #   s0=2
        if s1<=0:
            s1=0
        #elif s1>0 and s1<2:
        #   s1=2
        
        b+=s0
        b+=s1
        earning=0

        if s0>0:
            #we bet on player 0
            n_bets[0]+=1

            if bets.loc[i,"label"]==1:
                #we lost
                n_bets[2]+=1
                #print("Lost this one...")

            elif bets.loc[i,"label"]==0:
                #we won
                earning=float(s0)*float(bets.loc[i,"odd0"])
                r+=earning
                n_bets[1]+=1
                #print("Yess! Won {}€".format(earning))

                #if(earning>5):
                #    print("\n\t***** BIG WIN ALERT! *****\n")

        elif s1>0:
            #we bet on player 1
            n_bets[0]+=1

            if bets.loc[i,"label"]==0:
                #we lost
                n_bets[2]+=1
                #print("Lost this one...")

            elif bets.loc[i,"label"]==1:
                #we won
                earning=float(s1)*float(bets.loc[i,"odd1"])
                r+=earning
                n_bets[1]+=1
                #print("Yess! Won {}€".format(earning))

                #if(earning>5):
                #    print("\n\t***** BIG WIN ALERT! *****\n")
        else:
            pass


        budget=budget-s0-s1+earning
        y.append(budget)

    #print("\n***")
    print("\tAfter {} matches at disposal: \n\t-bets placed: {}\n\t-won: {}\n\t-lost: {}\n".format(bets.shape[0], n_bets[0], n_bets[1], n_bets[2]))
    print("\tFinal budget: {}€".format(round(budget,2)))
    print("\tAmount staked on bets: {}€\n\tReturn from bets: {}€".format(round(b,2),round(r,2)))
    print("\n\tROI: {}%\n".format(round((r-b)/b*100,2)))
    #print("\n***\n")
    """
    fig=plt.figure()
    plt.plot(x,y,'b')
    #plt.legend(loc='upper right',fontsize=10)
    plt.xlabel("Bet no.",fontsize=10)
    plt.ylabel("Budget",fontsize=10)
    plt.title("Budget evolution during betting streak", fontsize=15)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    #plt.ylim(0,0.2)
    #plt.xlim(-1,1)
    plt.grid()
    plt.show()
    """            

def trivial_bet(bets):
    # bet on player favoured by the model
    #print(bets.loc[0,:])
    x=range(bets.shape[0])
    y=[]
    budget=100
    b=0 #amount placed on bets
    r=0 #return
    q=1 #max bet size
    n_bets=[0,0,0] #placed, won, lost
    #print("Starting with: {}€".format(b))
    #print("\n...betting ongoing with Kelly criterion...\n")
    for i in range(bets.shape[0]):

        #print(bets.loc[i,:])

        #print("\n Currently betting on {} vs {}:\n\t- ML estimated probabilites: {} vs {}\n\t- B365 odds: {} vs {}".\
        #   format(bets.loc[i,"p0"],bets.loc[i,"p1"],bets.loc[i,"prob0"],bets.loc[i,"prob1"],bets.loc[i,"odd0"],bets.loc[i,"odd1"]))

        #evaluate implied probabilities from odds
        p0_ip=1/bets.loc[i,"odd0"]
        p1_ip=1/bets.loc[i,"odd1"]

        #print("P_bookies - player 0 to win: {}, player 1 to win: {}".format(p0_ip,p1_ip))

        s0=0
        if bets.loc[i,"prob0"]>=bets.loc[i,"prob1"]: 
            #s0=float(round(q*((bets.loc[i,"prob0"]*bets.loc[i,"odd0"]-1)/(bets.loc[i,"odd0"]-1)),2))
            s0=1
            #print("Betting {} on player 0".format(s0))
        
        s1=0
        if bets.loc[i,"prob1"]>bets.loc[i,"prob0"]:
            s1=1
            #s1=float(round(q*((bets.loc[i,"prob1"]*bets.loc[i,"odd1"]-1)/(bets.loc[i,"odd1"]-1)),2))
            #print("Betting {} on player 1".format(s1))
            
        if s0<=0:
            s0=0
        #elif s0>0 and s0<2: #min quota: 2€
        #   s0=2
        if s1<=0:
            s1=0
        #elif s1>0 and s1<2:
        #   s1=2
        
        b+=s0
        b+=s1
        earning=0

        if s0>0:
            #we bet on player 0
            n_bets[0]+=1

            if bets.loc[i,"label"]==1:
                #we lost
                n_bets[2]+=1
                #print("Lost this one...")

            elif bets.loc[i,"label"]==0:
                #we won
                earning=float(s0)*float(bets.loc[i,"odd0"])
                r+=earning
                n_bets[1]+=1
                #print("Yess! Won {}€".format(earning))

                #if(earning>5):
                #    print("\n\t***** BIG WIN ALERT! *****\n")

        elif s1>0:
            #we bet on player 1
            n_bets[0]+=1

            if bets.loc[i,"label"]==0:
                #we lost
                n_bets[2]+=1
                #print("Lost this one...")

            elif bets.loc[i,"label"]==1:
                #we won
                earning=float(s1)*float(bets.loc[i,"odd1"])
                r+=earning
                n_bets[1]+=1
                #print("Yess! Won {}€".format(earning))

                #if(earning>5):
                #    print("\n\t***** BIG WIN ALERT! *****\n")
        else:
            pass


        budget=budget-s0-s1+earning
        y.append(budget)

    #print("\n***")
    print("\tAfter {} matches at disposal: \n\t-bets placed: {}\n\t-won: {}\n\t-lost: {}\n".format(bets.shape[0], n_bets[0], n_bets[1], n_bets[2]))
    print("\tFinal budget: {}€".format(round(budget,2)))
    print("\tAmount staked on bets: {}€\n\tReturn from bets: {}€".format(round(b,2),round(r,2)))
    print("\n\tROI: {}%\n".format(round((r-b)/b*100,2)))


def trivial_bet2(bets):
    # bet on player favoured by the odds
    #print(bets.loc[0,:])
    x=range(bets.shape[0])
    y=[]
    budget=100
    b=0 #amount placed on bets
    r=0 #return
    q=1 #max bet size
    n_bets=[0,0,0] #placed, won, lost
    #print("Starting with: {}€".format(b))
    #print("\n...betting ongoing with Kelly criterion...\n")
    for i in range(bets.shape[0]):

        #print(bets.loc[i,:])

        #print("\n Currently betting on {} vs {}:\n\t- ML estimated probabilites: {} vs {}\n\t- B365 odds: {} vs {}".\
        #   format(bets.loc[i,"p0"],bets.loc[i,"p1"],bets.loc[i,"prob0"],bets.loc[i,"prob1"],bets.loc[i,"odd0"],bets.loc[i,"odd1"]))

        #evaluate implied probabilities from odds
        p0_ip=1/bets.loc[i,"odd0"]
        p1_ip=1/bets.loc[i,"odd1"]

        #print("P_bookies - player 0 to win: {}, player 1 to win: {}".format(p0_ip,p1_ip))

        s0=0
        if p0_ip>=p1_ip: 
            #s0=float(round(q*((bets.loc[i,"prob0"]*bets.loc[i,"odd0"]-1)/(bets.loc[i,"odd0"]-1)),2))
            s0=1
            #print("Betting {} on player 0".format(s0))
        
        s1=0
        if p1_ip>p0_ip:
            s1=1
            #s1=float(round(q*((bets.loc[i,"prob1"]*bets.loc[i,"odd1"]-1)/(bets.loc[i,"odd1"]-1)),2))
            #print("Betting {} on player 1".format(s1))
            
        if s0<=0:
            s0=0
        #elif s0>0 and s0<2: #min quota: 2€
        #   s0=2
        if s1<=0:
            s1=0
        #elif s1>0 and s1<2:
        #   s1=2
        
        b+=s0
        b+=s1
        earning=0

        if s0>0:
            #we bet on player 0
            n_bets[0]+=1

            if bets.loc[i,"label"]==1:
                #we lost
                n_bets[2]+=1
                #print("Lost this one...")

            elif bets.loc[i,"label"]==0:
                #we won
                earning=float(s0)*float(bets.loc[i,"odd0"])
                r+=earning
                n_bets[1]+=1
                #print("Yess! Won {}€".format(earning))

                #if(earning>5):
                #    print("\n\t***** BIG WIN ALERT! *****\n")

        elif s1>0:
            #we bet on player 1
            n_bets[0]+=1

            if bets.loc[i,"label"]==0:
                #we lost
                n_bets[2]+=1
                #print("Lost this one...")

            elif bets.loc[i,"label"]==1:
                #we won
                earning=float(s1)*float(bets.loc[i,"odd1"])
                r+=earning
                n_bets[1]+=1
                #print("Yess! Won {}€".format(earning))

                #if(earning>5):
                #    print("\n\t***** BIG WIN ALERT! *****\n")
        else:
            pass


        budget=budget-s0-s1+earning
        y.append(budget)

    #print("\n***")
    print("\tAfter {} matches at disposal: \n\t-bets placed: {}\n\t-won: {}\n\t-lost: {}\n".format(bets.shape[0], n_bets[0], n_bets[1], n_bets[2]))
    print("\tFinal budget: {}€".format(round(budget,2)))
    print("\tAmount staked on bets: {}€\n\tReturn from bets: {}€".format(round(b,2),round(r,2)))
    print("\n\tROI: {}%\n".format(round((r-b)/b*100,2)))