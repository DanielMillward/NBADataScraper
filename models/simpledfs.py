with pm.Model() as simple_dfs_model:
    alpha = pm.Gamma("alpha", alpha=3, beta=1)

    beta = pm.Gamma("beta", alpha=3, beta=5)

    mu = pm.Gamma("mu", alpha=alpha, beta=beta, shape=len(df.player_id.unique()))

    y = pm.Poisson("y", mu=mu[player_labels], observed=df.abs_dfs)
