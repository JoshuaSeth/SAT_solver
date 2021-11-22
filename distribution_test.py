from scipy.stats import anderson
import pickle
import scipy.stats as st


def get_best_distribution(data):
    dist_names = ["norm", "exponweib", "weibull_max", "weibull_min", "pareto", "genextreme", "f", "t", "rice", "weibull_min", "chi", "alpha", "betaprime", "burr", "erlang", "expon", "exponnorm", "exponweib", "foldnorm", "gengamma", "geninvgauss", "genpareto", "gumbel_r", "invgauss", "gumbel_r", "johnsonsb", "maxwell", "moyal", "mielke", "ncf", "powerlognorm", "rayleigh", "truncnorm", "wald"]
    dist_results = []
    params = {}
    for dist_name in dist_names:
        dist = getattr(st, dist_name)
        param = dist.fit(data)

        params[dist_name] = param
        # Applying the Kolmogorov-Smirnov test
        D, p = st.kstest(data, dist_name, args=param)
        # print("p value for "+dist_name+" = "+str(p))
        dist_results.append((dist_name, p))

    # select the best fitted distribution
    best_dist, best_p = (max(dist_results, key=lambda item: item[1]))
    # store the name of the best fit and its p value

    # print("Best fitting distribution: "+str(best_dist))
    # print("Best p value: "+ str(best_p))
    # print("Parameters for the best fit: "+ str(params[best_dist]))

    return best_dist, best_p, params[best_dist]

# with open('experiment_results/4x4_jw.txt', 'rb') as f:
#     data = pickle.load(f)
#     # data = [item.total_seconds() for item in data]
#     print(get_best_distribution(data))