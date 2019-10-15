from sklearn.model_selection import train_test_split

from headliner.model import SummarizerAttention
from headliner.model.summarizer_transformer import SummarizerTransformer
from headliner.training_runner import read_data_json

if __name__ == '__main__':
    path_to_model = '/Users/cschaefe/saved_models/att_512_7'
    summarizer = SummarizerAttention.load(path_to_model)
    data_raw = read_data_json('/Users/cschaefe/datasets/welt_dedup.json', 2000)
    train_data, val_data = train_test_split(data_raw, test_size=500, shuffle=True, random_state=42)

    for i in range(100):
        text_input, text_output = val_data[i]
        pred_text = summarizer.predict(text_input)
        print('\n\n(input) {}'.format(text_input))
        print('\n(target) {}'.format(text_output))
        print('\n(pred) {}'.format(pred_text))

    while True:
        text = input('\nEnter text: ')
        prediction_vecs = summarizer.predict_vectors(text, '')
        tokens_input = prediction_vecs['preprocessed_text'][0].split()
        print('\n')
        print(prediction_vecs['predicted_text'])
        print('\n')

