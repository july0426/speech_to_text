from collections import Counter
import sys

# make a copy of original stdout route
stdout_backup = sys.stdout
# define the log file that receives your log info
log_file = open("/home/wwwroot/show_caller_audio/message.log", "a")
# redirect print output to log file
sys.stdout = log_file


# any command line that you will execute
a = {'status': {'reason': None, 'code': 1000},
     'timestamps': [[u'there', 4.08, 4.25], [u'will', 4.25, 4.41], [u'be', 4.41, 4.53],
                    [u'good', 4.72, 5.1], [u'right', 7.34, 7.55], [u'and', 9.75, 9.91], [u'these', 9.91, 10.14],
                    [u'are', 10.38, 10.46], [u'my', 10.46, 10.65], [u'friends', 10.65, 11.11], [u'the', 12.61, 12.79],
                    [u'whole', 12.79, 13.09], [u'I', 15.82, 15.92], [u'mean', 15.92, 16.17], [u'these', 16.17, 16.41],
                    [u'are', 16.41, 16.48], [u'hello', 18.03, 18.39], [u'will', 18.78, 18.95], [u'come', 18.95, 19.23],
                    [u'along', 20.48, 20.76], [u'you', 20.76, 20.89], [u'know', 20.89, 21.03], [u'but', 21.03, 21.22],
                    [u'a', 21.22, 21.28], [u'lot', 21.28, 21.48], [u'of', 21.48, 21.54], [u'another', 21.54, 21.98],
                    [u'one', 21.98, 22.23], [u'how', 23.15, 23.39], [u'do', 23.39, 23.51], [u'you', 23.51, 23.7],
                    [u'what', 24.37, 24.57], [u'do', 24.57, 24.66], [u'you', 24.74, 24.96], [u'know', 24.96, 25.1],
                    [u'anyone', 25.1, 25.53], [u'with', 25.53, 25.65], [u'the', 25.96, 26.34], [u'you', 28.97, 29.12],
                    [u'want', 29.12, 29.33], [u'your', 29.33, 29.63], [u'money', 29.63, 29.81], [u'behind', 29.81, 30.16],
                    [u'it', 30.16, 30.22], [u'three', 31.66, 32.14], [u'hundred', 32.71, 33.16], [u'I', 34.05, 34.21],
                    [u'know', 34.21, 34.71], [u'you', 36.27, 36.33], [u'guys', 36.33, 36.56], [u'know', 36.96, 37.1],
                    [u'me', 37.1, 37.42], [u'I', 39.83, 39.86], [u'made', 39.86, 40.31], [u'the', 41.9, 42.08],
                    [u'large', 42.08, 42.33], [u'number', 42.33, 42.62], [u'ninety', 42.62, 43.02], [u'and', 44.06, 44.33],
                    [u'I', 44.33, 44.39], [u'mean', 45.4, 45.67], [u'you', 46.35, 46.5], [u'know', 46.5, 46.61],
                    [u'I', 46.61, 46.71], [u'mean', 46.71, 46.98], [u'I', 46.98, 47.02], [u'know', 47.02, 47.12],
                    [u'you', 47.12, 47.49], [u'yeah', 49.82, 50.23], [u'whose', 50.92, 51.22], [u'phone', 51.22, 51.4],
                    [u'number', 51.4, 51.68], [u'one', 51.68, 51.87], [u'in', 51.87, 52.13], [u'your', 52.13, 52.31],
                    [u'head', 52.31, 52.49], [u'had', 52.86, 53.24], [u'yeah', 55.82, 55.99], [u'he', 55.99, 56.51],
                    [u'and', 58.95, 59.2], [u'even', 59.2, 59.39], [u'the', 61.01, 61.48], [u'the', 62.99, 63.33],
                    [u'you', 65.96, 66.06], [u'will', 66.06, 66.35], [u'need', 66.35, 66.57], [u'one', 66.57, 66.71],
                    [u'another', 66.71, 67.37], [u'what', 68.79, 68.98], [u'are', 68.98, 69.29], [u'you', 69.29, 69.43],
                    [u'the', 70.29, 70.39], [u'men', 70.39, 70.7], [u'long', 70.7, 71.07], [u'why', 73.61, 73.77],
                    [u"won't", 73.77, 74.22], [u'they', 75.11, 75.28], [u'do', 75.28, 75.36], [u'not', 75.36, 75.65],
                    [u'one', 76.89, 77.08], [u'of', 77.08, 77.16], [u'my', 77.34, 77.51], [u'family', 78.12, 78.77],
                    [u'similar', 78.93, 79.53], [u'to', 79.53, 79.63], [u'this', 79.63, 79.83], [u'one', 79.83, 79.99],
                    [u'woman', 79.99, 80.5], [u'me', 83.13, 83.38], [u'well', 86.03, 86.31], [u'number', 87.3, 87.71],
                    [u'on', 87.71, 87.96], [u'it', 87.96, 88.1], [u'in', 88.1, 88.25], [u'one', 88.25, 88.59],
                    [u'yeah', 90.23, 90.69], [u'that', 99.89, 100.15], [u'one', 100.15, 100.3], [u'guy', 100.3, 100.43],
                    [u'that', 100.43, 100.66], [u'will', 100.66, 100.8], [u'only', 100.8, 101.12], [u'no', 102.98, 103.17]],
     'hypothesis': u"there will be good ,right ,and these are my friends ,the whole ,I mean these are ,hello will come along you know but a lot of another one ,how do you what do you know anyone with the ,you want your money behind it ,three hundred ,I know ,you guys know me ,I made ,the large number ninety ,and I mean you know I mean I know you ,yeah whose phone number one in your head had ,yeah he ,and even ,the ,the ,you will need one another ,what are you ,the men long ,why won't ,they do not ,one of my family similar to this one woman ,me ,well ,number on it in one ,yeah ,that one guy that will only ,no ,",
     'speaker_labels': [
         {u'confidence': 0.667, u'speaker': 0, u'from': 4.08}, {u'confidence': 0.667, u'speaker': 0, u'from': 4.25},
         {u'confidence': 0.667, u'speaker': 0, u'from': 4.41}, {u'confidence': 0.667, u'speaker': 1, u'from': 4.72},
         {u'confidence': 0.536, u'speaker': 2, u'from': 7.34}, {u'confidence': 0.351, u'speaker': 0, u'from': 9.75},
         {u'confidence': 0.351, u'speaker': 0, u'from': 9.91}, {u'confidence': 0.382, u'speaker': 3, u'from': 10.38},
         {u'confidence': 0.382, u'speaker': 3, u'from': 10.46}, {u'confidence': 0.382, u'speaker': 3, u'from': 10.65},
         {u'confidence': 0.39, u'speaker': 1, u'from': 9.75}, {u'confidence': 0.39, u'speaker': 1, u'from': 9.91},
         {u'confidence': 0.389, u'speaker': 1, u'from': 10.38}, {u'confidence': 0.389, u'speaker': 1, u'from': 10.46},
         {u'confidence': 0.389, u'speaker': 1, u'from': 10.65}, {u'confidence': 0.468, u'speaker': 0, u'from': 12.61},
         {u'confidence': 0.468, u'speaker': 0, u'from': 12.79}, {u'confidence': 0.411, u'speaker': 0, u'from': 15.82},
         {u'confidence': 0.411, u'speaker': 0, u'from': 15.92}, {u'confidence': 0.411, u'speaker': 0, u'from': 16.17},
         {u'confidence': 0.411, u'speaker': 0, u'from': 16.41}, {u'confidence': 0.421, u'speaker': 0, u'from': 4.72},
         {u'confidence': 0.532, u'speaker': 0, u'from': 9.75}, {u'confidence': 0.532, u'speaker': 0, u'from': 9.91},
         {u'confidence': 0.509, u'speaker': 0, u'from': 10.38}, {u'confidence': 0.509, u'speaker': 0, u'from': 10.46},
         {u'confidence': 0.509, u'speaker': 0, u'from': 10.65}, {u'confidence': 0.619, u'speaker': 2, u'from': 18.03},
         {u'confidence': 0.375, u'speaker': 0, u'from': 18.78}, {u'confidence': 0.375, u'speaker': 0, u'from': 18.95},
         {u'confidence': 0.54, u'speaker': 2, u'from': 20.48}, {u'confidence': 0.54, u'speaker': 2, u'from': 20.76},
         {u'confidence': 0.54, u'speaker': 2, u'from': 20.89}, {u'confidence': 0.54, u'speaker': 2, u'from': 21.03},
         {u'confidence': 0.54, u'speaker': 2, u'from': 21.22}, {u'confidence': 0.54, u'speaker': 2, u'from': 21.28},
         {u'confidence': 0.54, u'speaker': 2, u'from': 21.48}, {u'confidence': 0.54, u'speaker': 2, u'from': 21.54},
         {u'confidence': 0.54, u'speaker': 2, u'from': 21.98}, {u'confidence': 0.551, u'speaker': 2, u'from': 23.15},
         {u'confidence': 0.551, u'speaker': 2, u'from': 23.39}, {u'confidence': 0.551, u'speaker': 2, u'from': 23.51},
         {u'confidence': 0.486, u'speaker': 2, u'from': 24.37}, {u'confidence': 0.486, u'speaker': 2, u'from': 24.57},
         {u'confidence': 0.601, u'speaker': 2, u'from': 24.74}, {u'confidence': 0.601, u'speaker': 2, u'from': 24.96}, {u'confidence': 0.601, u'speaker': 2, u'from': 25.1}, {u'confidence': 0.601, u'speaker': 2, u'from': 25.53}, {u'confidence': 0.637, u'speaker': 2, u'from': 25.96}, {u'confidence': 0.501, u'speaker': 2, u'from': 28.97}, {u'confidence': 0.501, u'speaker': 2, u'from': 29.12}, {u'confidence': 0.501, u'speaker': 2, u'from': 29.33}, {u'confidence': 0.501, u'speaker': 2, u'from': 29.63}, {u'confidence': 0.501, u'speaker': 2, u'from': 29.81}, {u'confidence': 0.501, u'speaker': 2, u'from': 30.16}, {u'confidence': 0.416, u'speaker': 1, u'from': 18.03}, {u'confidence': 0.324, u'speaker': 2, u'from': 18.78}, {u'confidence': 0.324, u'speaker': 2, u'from': 18.95}, {u'confidence': 0.354, u'speaker': 1, u'from': 20.48}, {u'confidence': 0.354, u'speaker': 1, u'from': 20.76}, {u'confidence': 0.354, u'speaker': 1, u'from': 20.89}, {u'confidence': 0.354, u'speaker': 1, u'from': 21.03}, {u'confidence': 0.354, u'speaker': 1, u'from': 21.22}, {u'confidence': 0.354, u'speaker': 1, u'from': 21.28}, {u'confidence': 0.354, u'speaker': 1, u'from': 21.48}, {u'confidence': 0.354, u'speaker': 1, u'from': 21.54}, {u'confidence': 0.354, u'speaker': 1, u'from': 21.98}, {u'confidence': 0.432, u'speaker': 1, u'from': 31.66}, {u'confidence': 0.432, u'speaker': 1, u'from': 32.71}, {u'confidence': 0.373, u'speaker': 2, u'from': 34.05}, {u'confidence': 0.373, u'speaker': 2, u'from': 34.21}, {u'confidence': 0.477, u'speaker': 0, u'from': 36.27}, {u'confidence': 0.477, u'speaker': 0, u'from': 36.33}, {u'confidence': 0.442, u'speaker': 2, u'from': 36.96}, {u'confidence': 0.442, u'speaker': 2, u'from': 37.1}, {u'confidence': 0.372, u'speaker': 0, u'from': 18.78}, {u'confidence': 0.372, u'speaker': 0, u'from': 18.95}, {u'confidence': 0.388, u'speaker': 2, u'from': 39.83}, {u'confidence': 0.388, u'speaker': 2, u'from': 39.86}, {u'confidence': 0.39, u'speaker': 0, u'from': 41.9}, {u'confidence': 0.39, u'speaker': 0, u'from': 42.08}, {u'confidence': 0.39, u'speaker': 0, u'from': 42.33}, {u'confidence': 0.39, u'speaker': 0, u'from': 42.62}, {u'confidence': 0.431, u'speaker': 2, u'from': 44.06}, {u'confidence': 0.431, u'speaker': 2, u'from': 44.33}, {u'confidence': 0.235, u'speaker': 2, u'from': 45.4}, {u'confidence': 0.48, u'speaker': 2, u'from': 46.35}, {u'confidence': 0.48, u'speaker': 2, u'from': 46.5}, {u'confidence': 0.48, u'speaker': 2, u'from': 46.61}, {u'confidence': 0.48, u'speaker': 2, u'from': 46.71}, {u'confidence': 0.48, u'speaker': 2, u'from': 46.98}, {u'confidence': 0.48, u'speaker': 2, u'from': 47.02}, {u'confidence': 0.48, u'speaker': 2, u'from': 47.12}, {u'confidence': 0.282, u'speaker': 0, u'from': 18.03}, {u'confidence': 0.428, u'speaker': 2, u'from': 18.78}, {u'confidence': 0.428, u'speaker': 2, u'from': 18.95}, {u'confidence': 0.355, u'speaker': 0, u'from': 20.48}, {u'confidence': 0.355, u'speaker': 0, u'from': 20.76}, {u'confidence': 0.355, u'speaker': 0, u'from': 20.89}, {u'confidence': 0.355, u'speaker': 0, u'from': 21.03}, {u'confidence': 0.355, u'speaker': 0, u'from': 21.22}, {u'confidence': 0.355, u'speaker': 0, u'from': 21.28}, {u'confidence': 0.355, u'speaker': 0, u'from': 21.48}, {u'confidence': 0.355, u'speaker': 0, u'from': 21.54}, {u'confidence': 0.355, u'speaker': 0, u'from': 21.98}, {u'confidence': 0.555, u'speaker': 0, u'from': 31.66}, {u'confidence': 0.418, u'speaker': 0, u'from': 32.71}, {u'confidence': 0.448, u'speaker': 2, u'from': 49.82}, {u'confidence': 0.574, u'speaker': 0, u'from': 50.92}, {u'confidence': 0.574, u'speaker': 0, u'from': 51.22}, {u'confidence': 0.574, u'speaker': 0, u'from': 51.4}, {u'confidence': 0.574, u'speaker': 0, u'from': 51.68}, {u'confidence': 0.574, u'speaker': 0, u'from': 51.87}, {u'confidence': 0.574, u'speaker': 0, u'from': 52.13}, {u'confidence': 0.574, u'speaker': 0, u'from': 52.31}, {u'confidence': 0.596, u'speaker': 0, u'from': 52.86}, {u'confidence': 0.647, u'speaker': 2, u'from': 55.82}, {u'confidence': 0.647, u'speaker': 2, u'from': 55.99}, {u'confidence': 0.462, u'speaker': 0, u'from': 58.95}, {u'confidence': 0.462, u'speaker': 0, u'from': 59.2}, {u'confidence': 0.573, u'speaker': 0, u'from': 61.01}, {u'confidence': 0.386, u'speaker': 2, u'from': 20.48}, {u'confidence': 0.386, u'speaker': 2, u'from': 20.76}, {u'confidence': 0.386, u'speaker': 2, u'from': 20.89}, {u'confidence': 0.386, u'speaker': 2, u'from': 21.03}, {u'confidence': 0.386, u'speaker': 2, u'from': 21.22}, {u'confidence': 0.386, u'speaker': 2, u'from': 21.28}, {u'confidence': 0.386, u'speaker': 2, u'from': 21.48}, {u'confidence': 0.386, u'speaker': 2, u'from': 21.54}, {u'confidence': 0.386, u'speaker': 2, u'from': 21.98}, {u'confidence': 0.533, u'speaker': 0, u'from': 62.99}, {u'confidence': 0.308, u'speaker': 0, u'from': 20.48}, {u'confidence': 0.308, u'speaker': 0, u'from': 20.76}, {u'confidence': 0.308, u'speaker': 0, u'from': 20.89}, {u'confidence': 0.308, u'speaker': 0, u'from': 21.03}, {u'confidence': 0.308, u'speaker': 0, u'from': 21.22}, {u'confidence': 0.308, u'speaker': 0, u'from': 21.28}, {u'confidence': 0.308, u'speaker': 0, u'from': 21.48}, {u'confidence': 0.308, u'speaker': 0, u'from': 21.54}, {u'confidence': 0.308, u'speaker': 0, u'from': 21.98}, {u'confidence': 0.526, u'speaker': 2, u'from': 65.96}, {u'confidence': 0.526, u'speaker': 2, u'from': 66.06}, {u'confidence': 0.526, u'speaker': 2, u'from': 66.35}, {u'confidence': 0.526, u'speaker': 2, u'from': 66.57}, {u'confidence': 0.526, u'speaker': 2, u'from': 66.71}, {u'confidence': 0.621, u'speaker': 2, u'from': 68.79}, {u'confidence': 0.621, u'speaker': 2, u'from': 68.98}, {u'confidence': 0.621, u'speaker': 2, u'from': 69.29}, {u'confidence': 0.466, u'speaker': 0, u'from': 70.29}, {u'confidence': 0.466, u'speaker': 0, u'from': 70.39}, {u'confidence': 0.466, u'speaker': 0, u'from': 70.7}, {u'confidence': 0.359, u'speaker': 0, u'from': 7.34}, {u'confidence': 0.263, u'speaker': 0, u'from': 18.78}, {u'confidence': 0.263, u'speaker': 0, u'from': 18.95}, {u'confidence': 0.312, u'speaker': 0, u'from': 45.4}, {u'confidence': 0.251, u'speaker': 0, u'from': 49.82}, {u'confidence': 0.59, u'speaker': 2, u'from': 73.61}, {u'confidence': 0.59, u'speaker': 2, u'from': 73.77}, {u'confidence': 0.441, u'speaker': 0, u'from': 75.11}, {u'confidence': 0.441, u'speaker': 0, u'from': 75.28}, {u'confidence': 0.441, u'speaker': 0, u'from': 75.36}, {u'confidence': 0.34, u'speaker': 2, u'from': 7.34}, {u'confidence': 0.423, u'speaker': 2, u'from': 18.78}, {u'confidence': 0.423, u'speaker': 2, u'from': 18.95}, {u'confidence': 0.3, u'speaker': 2, u'from': 45.4}, {u'confidence': 0.462, u'speaker': 2, u'from': 49.82}, {u'confidence': 0.52, u'speaker': 2, u'from': 76.89}, {u'confidence': 0.52, u'speaker': 2, u'from': 77.08}, {u'confidence': 0.632, u'speaker': 2, u'from': 77.34}, {u'confidence': 0.6, u'speaker': 2, u'from': 78.12}, {u'confidence': 0.412, u'speaker': 2, u'from': 78.93}, {u'confidence': 0.412, u'speaker': 2, u'from': 79.53}, {u'confidence': 0.412, u'speaker': 2, u'from': 79.63}, {u'confidence': 0.412, u'speaker': 2, u'from': 79.83}, {u'confidence': 0.412, u'speaker': 2, u'from': 79.99}, {u'confidence': 0.628, u'speaker': 2, u'from': 83.13}, {u'confidence': 0.259, u'speaker': 0, u'from': 18.78}, {u'confidence': 0.259, u'speaker': 0, u'from': 18.95}, {u'confidence': 0.279, u'speaker': 0, u'from': 78.93}, {u'confidence': 0.279, u'speaker': 0, u'from': 79.53}, {u'confidence': 0.279, u'speaker': 0, u'from': 79.63}, {u'confidence': 0.279, u'speaker': 0, u'from': 79.83}, {u'confidence': 0.279, u'speaker': 0, u'from': 79.99}, {u'confidence': 0.463, u'speaker': 2, u'from': 86.03}, {u'confidence': 0.429, u'speaker': 2, u'from': 18.03}, {u'confidence': 0.362, u'speaker': 2, u'from': 18.78}, {u'confidence': 0.362, u'speaker': 2, u'from': 18.95}, {u'confidence': 0.28, u'speaker': 2, u'from': 20.48}, {u'confidence': 0.28, u'speaker': 2, u'from': 20.76}, {u'confidence': 0.28, u'speaker': 2, u'from': 20.89}, {u'confidence': 0.28, u'speaker': 2, u'from': 21.03}, {u'confidence': 0.28, u'speaker': 2, u'from': 21.22}, {u'confidence': 0.28, u'speaker': 2, u'from': 21.28}, {u'confidence': 0.28, u'speaker': 2, u'from': 21.48}, {u'confidence': 0.28, u'speaker': 2, u'from': 21.54}, {u'confidence': 0.28, u'speaker': 2, u'from': 21.98}, {u'confidence': 0.271, u'speaker': 2, u'from': 32.71}, {u'confidence': 0.16, u'speaker': 2, u'from': 62.99}, {u'confidence': 0.256, u'speaker': 2, u'from': 75.11}, {u'confidence': 0.256, u'speaker': 2, u'from': 75.28}, {u'confidence': 0.256, u'speaker': 2, u'from': 75.36}, {u'confidence': 0.458, u'speaker': 2, u'from': 78.93}, {u'confidence': 0.458, u'speaker': 2, u'from': 79.53}, {u'confidence': 0.458, u'speaker': 2, u'from': 79.63}, {u'confidence': 0.458, u'speaker': 2, u'from': 79.83}, {u'confidence': 0.458, u'speaker': 2, u'from': 79.99}, {u'confidence': 0.612, u'speaker': 0, u'from': 87.3}, {u'confidence': 0.612, u'speaker': 0, u'from': 87.71}, {u'confidence': 0.612, u'speaker': 0, u'from': 87.96}, {u'confidence': 0.612, u'speaker': 0, u'from': 88.1}, {u'confidence': 0.612, u'speaker': 0, u'from': 88.25}, {u'confidence': 0.371, u'speaker': 0, u'from': 7.34}, {u'confidence': 0.33, u'speaker': 0, u'from': 18.03}, {u'confidence': 0.429, u'speaker': 0, u'from': 20.48}, {u'confidence': 0.429, u'speaker': 0, u'from': 20.76}, {u'confidence': 0.429, u'speaker': 0, u'from': 20.89}, {u'confidence': 0.429, u'speaker': 0, u'from': 21.03}, {u'confidence': 0.429, u'speaker': 0, u'from': 21.22}, {u'confidence': 0.429, u'speaker': 0, u'from': 21.28}, {u'confidence': 0.429, u'speaker': 0, u'from': 21.48}, {u'confidence': 0.429, u'speaker': 0, u'from': 21.54}, {u'confidence': 0.429, u'speaker': 0, u'from': 21.98}, {u'confidence': 0.474, u'speaker': 0, u'from': 32.71}, {u'confidence': 0.567, u'speaker': 0, u'from': 62.99}, {u'confidence': 0.497, u'speaker': 0, u'from': 75.11}, {u'confidence': 0.497, u'speaker': 0, u'from': 75.28}, {u'confidence': 0.497, u'speaker': 0, u'from': 75.36}, {u'confidence': 0.313, u'speaker': 0, u'from': 78.93}, {u'confidence': 0.313, u'speaker': 0, u'from': 79.53}, {u'confidence': 0.313, u'speaker': 0, u'from': 79.63}, {u'confidence': 0.313, u'speaker': 0, u'from': 79.83}, {u'confidence': 0.313, u'speaker': 0, u'from': 79.99}, {u'confidence': 0.577, u'speaker': 2, u'from': 90.23}, {u'confidence': 0.308, u'speaker': 2, u'from': 7.34}, {u'confidence': 0.31, u'speaker': 0, u'from': 65.96}, {u'confidence': 0.31, u'speaker': 0, u'from': 66.06}, {u'confidence': 0.31, u'speaker': 0, u'from': 66.35}, {u'confidence': 0.31, u'speaker': 0, u'from': 66.57}, {u'confidence': 0.31, u'speaker': 0, u'from': 66.71}, {u'confidence': 0.334, u'speaker': 0, u'from': 99.89}, {u'confidence': 0.334, u'speaker': 0, u'from': 100.15}, {u'confidence': 0.334, u'speaker': 0, u'from': 100.3}, {u'confidence': 0.334, u'speaker': 0, u'from': 100.43}, {u'confidence': 0.334, u'speaker': 0, u'from': 100.66}, {u'confidence': 0.334, u'speaker': 0, u'from': 100.8}, {u'confidence': 0.394, u'speaker': 0, u'from': 7.34}, {u'confidence': 0.407, u'speaker': 0, u'from': 102.98}, {u'confidence': 0.407, u'speaker': 0, u'from': 102.98}]}
a['speaker_labels'].sort(key=lambda x:x['from']+x['confidence'])
spaker = a['speaker_labels']
temp = a['timestamps']
new_temp = {i[1]:i[0] for i in temp}
print new_temp
def delto(speak):
    lists = []
    for i in range(len(speak)-1):
        # print i
        if speak[i]['from'] == speak[i+1]['from']:
            lists.append(speak[i])
    for i in lists:
        speak.remove(i)
    # speak = list(set(speak) - set(lists))
delto(spaker)
text = []
for x in range(len(spaker)):
    i= spaker[x]
    if x == 0:
        text.append('speaker' + ' ' +str(i['speaker']) + ':' + new_temp[i['from']])
    elif x < len(spaker):
        if spaker[x]["speaker"] == spaker[x-1]["speaker"]:
            text.append(' ' + new_temp[i['from']])
            # print text
        else:
            text.append('\n' + 'speaker' + ' ' +str(i['speaker']) + ':' + new_temp[i['from']])
    # else:
    #     if spaker[x]["speaker"] == spaker[x-1]["speaker"]:
    #         text.append(' ' + new_temp[i['from']])
    #     else:
    #         text.append('\n' + 'speaker' + ' ' +str(i['speaker']) + ':' + new_temp[i['from']])
print text
print ''.join(text).strip('\n')


log_file.close()
# restore the output to initial pattern
sys.stdout = stdout_backup

print "Now this will be presented on screen"
# print spaker
# b = [
#     {u'to': 0.84, u'confidence': 0.508, u'speaker': 0, u'from': 0.46},
#     {u'to': 1.54, u'confidence': 0.415, u'speaker': 1, u'from': 1.14},
#     {u'to': 1.54, u'confidence': 0.478, u'speaker': 2, u'from': 1.14},
#     {u'to': 2.26, u'confidence': 0.423, u'speaker': 1, u'from': 1.79},
#     {u'to': 2.26, u'confidence': 0.441, u'speaker': 2, u'from': 1.79},
#     {u'to': 3.14, u'confidence': 0.467, u'speaker': 2, u'from': 2.89},
#     {u'to': 4.01, u'confidence': 0.467, u'speaker': 2, u'from': 3.14},
#     {u'to': 4.33, u'confidence': 0.467, u'speaker': 2, u'from': 4.01},
#     {u'to': 4.6, u'confidence': 0.467, u'speaker': 2, u'from': 4.33},
#     {u'to': 5.42, u'confidence': 0.512, u'speaker': 0, u'from': 5.06},
#     {u'to': 8.0, u'confidence': 0.515, u'speaker': 0, u'from': 7.64},
#     {u'to': 8.73, u'confidence': 0.467, u'speaker': 1, u'from': 8.34},
#     {u'to': 8.73, u'confidence': 0.494, u'speaker': 2, u'from': 8.34},
#     {u'to': 9.39, u'confidence': 0.458, u'speaker': 2, u'from': 8.92},
#     {u'to': 11.2, u'confidence': 0.486, u'speaker': 2, u'from': 10.36},
#     {u'to': 11.53, u'confidence': 0.486, u'speaker': 2, u'from': 11.2},
#     {u'to': 11.79, u'confidence': 0.486, u'speaker': 2, u'from': 11.53},
#     {u'to': 12.62, u'confidence': 0.651, u'speaker': 0, u'from': 12.24},
#     {u'to': 13.3, u'confidence': 0.366, u'speaker': 2, u'from': 12.94},
#     {u'to': 14.01, u'confidence': 0.448, u'speaker': 2, u'from': 13.66},
#     {u'to': 15.12, u'confidence': 0.65, u'speaker': 0, u'from': 14.85},
#     {u'to': 15.86, u'confidence': 0.492, u'speaker': 2, u'from': 15.47},
#     {u'to': 16.51, u'confidence': 0.497, u'speaker': 2, u'from': 16.07},
#     {u'to': 16.51, u'confidence': 0.497, u'speaker': 2, u'from': 16.07}
# ]
# c = Counter()
# for ch in b:
#     c[ch['from']] = c[ch['from']] + 1
# for i in b:
#     list_from = {}
#     if c[i["from"]] > 1:
#         list_from[i["from"]] = i
#
# # print c
#
