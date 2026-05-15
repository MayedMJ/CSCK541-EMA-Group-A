import random
import matplotlib.pyplot as plt

alphabet = 'abcdefghijklmnopqrstuvwxyz'
distribution = {letter: 0 for letter in alphabet}

for i in range(1000, 101000, 1000):
    for _ in range(i):
        letter = random.choice(alphabet)
        distribution[letter] += 1

    dict_to_list_of_tuples = list(distribution.items())
    sorted_distribution = sorted(dict_to_list_of_tuples, key=lambda x: x[1], reverse=True)

    highest_as_percentage = (sorted_distribution[0][1] / i) * 100
    lowest_as_percentage = (sorted_distribution[-1][1] / i) * 100
    difference_ratio = sorted_distribution[0][1]/sorted_distribution[-1][1] if sorted_distribution[-1][1] != 0 else float('inf')
    print(f"For choice of {i}: ratio = {round(difference_ratio, 3)}, percentage of most chosen = {round(highest_as_percentage, 2)}%, percentage of least chosen = {round(lowest_as_percentage, 2)}%")
    # Reset distribution for next iteration
    distribution = {letter: 0 for letter in alphabet}

choices = 100000
for _ in range(choices):
    letter = random.choice(alphabet)
    distribution[letter] += 1

dict_to_list_of_tuples = list(distribution.items())
sorted_distribution = sorted(dict_to_list_of_tuples, key=lambda x: x[1], reverse=True)

highest_as_percentage = (sorted_distribution[0][1] / i) * 100
lowest_as_percentage = (sorted_distribution[-1][1] / i) * 100
difference_ratio = sorted_distribution[0][1]/sorted_distribution[-1][1] if sorted_distribution[-1][1] != 0 else float('inf')
print(f"For choice of {i}: ratio = {round(difference_ratio, 3)}, percentage of most chosen = {round(highest_as_percentage, 2)}%, percentage of least chosen = {round(lowest_as_percentage, 2)}%")

frequency_of_frequencies = {}
for letter, count in distribution.items(): 
    if count not in frequency_of_frequencies: 
        frequency_of_frequencies[count] = 0 
    frequency_of_frequencies[count] += 1
plt.bar(frequency_of_frequencies.keys(), frequency_of_frequencies.values())
plt.xlabel('Frequency of Occurrence')
plt.ylabel('Number of Letters')
plt.title(f'Frequency of Frequencies for {choices} Random Choices')
plt.show() 



    

