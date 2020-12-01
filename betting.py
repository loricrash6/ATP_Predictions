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
            bets, amounts = [-1 if prediction<0.5 else +1 for prediction in predictions], [1]*len(predictions)
        
        if self.method=='better_odds':
            #bet a fixed amount when predicted probability of a player winning a match is higher than implied probability
            implied_probs_p1=[odds_p2[i]/(odds_p1[i]+odds_p2[i]) for i in range(len(predictions))]
            implied_probs_p2=[odds_p1[i]/(odds_p1[i]+odds_p2[i]) for i in range(len(predictions))]
            
            bets=[-1 if predictions[i]>implied_probs_p1[i] else +1 if 1-predictions[i]>implied_probs_p2[i] else 0 for i in range(len(predictions))]
            amounts=[0 if bet==0 else 1 for bet in bets]


        if self.method=='kelly':
            #bet a fraction 
            implied_probs_p1=[odds_p2[i]/(odds_p1[i]+odds_p2[i]) for i in range(len(predictions))]
            implied_probs_p2=[odds_p1[i]/(odds_p1[i]+odds_p2[i]) for i in range(len(predictions))]

            bets=[-1 if predictions[i]>implied_probs_p1[i] else +1 if 1-predictions[i]>implied_probs_p2[i] else 0 for i in range(len(predictions))]
            amounts = [ 0 if bets[i]==0 else (predictions[i]*(odds_p1[i]+1)-1)/odds_p1[i] if bets[i]==-1 else (predictions[i]*(odds_p2[i]+1)-1)/odds_p2[i] for i in range(len(predictions)) ]

        print(f'Bets {sum(amounts)} over {sum([1 if amount>0 else 0 for amount in amounts])} games, out of {len(predictions)}')  
        return bets, amounts
    
    def roi(self, predictions, odds_p1, odds_p2, winners):
        "winners: array 0 if p1, 1 if p2"
        bets, amounts = self.bet(predictions,odds_p1, odds_p2)

        gains=[0]*len(bets)

        nb_won = 0

        for i in range(len(bets)):
            if bets[i]==-1 and winners[i]==0: #winning bet on p1
                gains[i] = odds_p1[i]*amounts[i]
                nb_won += 1
            if bets[i]==1 and winners[i]==1: #winning bet on p2
                gains[i] = odds_p2[i]*amounts[i]
                nb_won += 1
            else:
                gains[i] = 0

        gains = [odds_p1[i]*amounts[i] if bets[i]==-1 and winners[i]==0 else odds_p2[i]*amounts[i] if bets[i]==1 and winners[i]==1 else 0 for i in range(len(bets))]
        
        print(f'{nb_won} winning bets, gains of {sum(gains)} investing {sum(amounts)}')
        return (sum(gains)-sum(amounts))/sum(amounts)

            