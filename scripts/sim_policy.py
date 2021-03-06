import os.path as osp
import argparse
import pickle
import joblib
import tensorflow as tf
from rllab.policies.uniform_control_policy import UniformControlPolicy
from rllab.sampler.utils import rollout
from rllab.misc.ext import set_seed

import numpy as np


from sandbox.envs.maze.maze_ant.ant_maze_env import AntMazeEnv
from rllab.envs.normalized_env import normalize
from sandbox.envs.goal_env import GoalExplorationEnv
from sandbox.envs.base import FixedStateGenerator, UniformListStateGenerator, UniformStateGenerator

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str,
                        help='path to the snapshot file')
    parser.add_argument('--max_path_length', type=int, default=1000,
                        help='Max length of rollout')
    parser.add_argument('--speedup', type=float, default=1,
                        help='Speedup')
    parser.add_argument('--seed', type=int, default=-1,
                        help='Fixed random seed')
    parser.add_argument("-is", '--init_state', type=str,
                        help='vector of init_state')
    parser.add_argument("-cf", '--collection_file', type=str,
                        help='path to the pkl file with start positions Collection')
    parser.add_argument("-r", '--random_policy', action='store_true', default=False,
                        help='use random actions')
    parser.add_argument("-d", '--deterministic', action='store_true', default=False,
                        help='whether to use a deterministic policy')
    parser.add_argument("-g", '--using_gym', action='store_true', default=False,
                             help='using gym')
    args = parser.parse_args()

    policy = None
    env = None

    # If the snapshot file use tensorflow, do:
    # import tensorflow as tf
    # with tf.Session():
    #     [rest of the code]
    # while True:
    if args.seed >= 0:
        set_seed(args.seed)
    if args.collection_file:
        all_feasible_starts = pickle.load(open(args.collection_file, 'rb'))

    with tf.Session() as sess:
        data = joblib.load(args.file)
        if "algo" in data:
            policy = data["algo"].policy
            env = data["algo"].env
        else:
            policy = data['policy']
            env = data['env']

        if args.random_policy:
            policy = UniformControlPolicy(env_spec=env.spec)

        while True:
            if args.init_state:
                from sandbox.envs.base import FixedStateGenerator
                env.update_start_generator(FixedStateGenerator(args.init_state))
            elif args.collection_file:
                from sandbox.envs.base import UniformListStateGenerator
                init_states = all_feasible_starts.sample(1000)
                env.update_start_generator(UniformListStateGenerator(init_states))
            if args.deterministic:
                with policy.set_std_to_0():
                    path = rollout(env, policy, max_path_length=args.max_path_length,
                                   animated=True, speedup=args.speedup)
            else:
                path = rollout(env, policy, max_path_length=args.max_path_length,
                               animated=True, speedup=args.speedup, using_gym=args.using_gym)
            print(len(path["rewards"]))
            print(path["rewards"][-1])