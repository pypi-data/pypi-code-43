



class GeneralizedAdvantageEstimator:

    def estimate(self, states, internals, reward):

            return self.discounted_cumulative_reward(terminal=terminal, reward=reward)

            self.baseline_mode == 'full'

        else:
            if self.baseline_mode == 'states':
                state_value = self.baseline.predict(states=states, internals=internals)

            elif self.baseline_mode == 'network':
                embedding = self.network.apply(x=states, internals=internals)
                state_value = self.baseline.predict(
                    states=tf.stop_gradient(input=embedding), internals=internals
                )


            if self.gae_lambda is None:
                reward = self.discounted_cumulative_reward(terminal=terminal, reward=reward)

            else:
                next_state_value = tf.concat(values=(state_value[1:], (0.0,)), axis=0)
                zeros = tf.zeros_like(tensor=next_state_value)
                next_state_value = tf.where(condition=terminal, x=zeros, y=next_state_value)
                discount = self.discount.value()
                td_residual = reward + discount * next_state_value - state_value
                gae_lambda = self.gae_lambda.value()
                advantage = self.discounted_cumulative_reward(
                    terminal=terminal, reward=td_residual, discount=(discount * gae_lambda)
                )
