from headliner.model.summarizer_bert import SummarizerBert

if __name__ == '__main__':
    path_to_model = '/tmp/summarizer_20191023_115209'
    summarizer = SummarizerBert.load(path_to_model)

    while True:
        text = input('\nEnter text: ')
        prediction_vecs = summarizer.predict_vectors(text, '')
        tokens_input = prediction_vecs['preprocessed_text'][0].split()
        print('\n')
        print(prediction_vecs['predicted_text'])
        print('\n')

