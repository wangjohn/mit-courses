
    def update(self, obs):
        result = {}
        
        cached_belief = {}
        cached_obs_model = {}
        totalBelief = 0
        for state in self.belief.support():
            cached_belief[state] = self.belief.prob(state)
            cached_obs_model[state] = self.obsModel(state).prob(obs)
            totalBelief += cached_belief[state] * cached_obs_model[state]
            
        for state in self.belief.support():
            newProb = float(cached_belief[state] * cached_obs_model[state]) / totalBelief
            result[state] = newProb

        final_result = {}
        for state, stateProb in result.iteritems():
            transDist = self.transModel(state)
            for newState in transDist.support():
                prob = stateProb * transDist.prob(newState)
                
                if newState in result:
                    final_result[newState] += prob
                else:
                    final_result[newState] = prob
        self.belief = DDist(final_result)

    def observe(self, obs):
        result = {}
        totalBelief = 0
        for state in self.belief.support():
            totalBelief += self.belief.prob(state) * self.obsModel(state).prob(obs)
            
        for state in self.belief.support():
            newProb = float(self.obsModel(state).prob(obs) * self.belief.prob(state)) / totalBelief
            result[state] = newProb
        
        self.belief = DDist(result)
