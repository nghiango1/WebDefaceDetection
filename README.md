# WebDefaceDetection

A research project aim to build a new Detection tool using machine learning. Machine translate of the Research thesis can be found here: https://drive.google.com/file/d/1BrK4KZSfYeVjzzUKvmr7bjtyXWeUOw8P/view?usp=sharing

## Quick walkthrough

![detection_model](https://github.com/nghiango1/WebDefaceDetection/assets/31164703/a4d3a7fd-fe4d-4805-82ec-d14258c3d630)

After all Reason, Definition and Theory, the main implementing start at `CHƯƠNG (CHAPTER) 3 INSTALLATION AND TESTING`. I will explain more on how source code in this repo reflect on the thesis detection model proposed thesis. The main part of thesis come from building classifier machine learning model:

### Data gathering

Web scrapping automation using Javascript, puppeteer:
- The URLs that need to be monitored are automatically processed by the web crawler, and the returned results include the resource and HTML source code;
- The website resources are extracted as the detection signature set.

**Source**: `archive_Script-hashlog.js`
**Input**: URL file list, can use provided `200-safe-vn.txt`, `200-deface.csv` or using your own, edit the path directly in the source code
```js
async function main(){
	let all_urls;
	all_urls = (await fse.readFile( '200-safe-vn.txt', 'utf-8')).split('\r\n');
```
**Output**: Run data:
- `fail-log.csv`: Containt list of page URL that errors when crawling
- Page data: Every page data will be store in they own `saved/<url_sanitize>` directory (all character that be blocked by window will be change to `_`)
  - `saved_responsed_file/`: All page loaded resource will be pull and store in this directory with their correspond hash name
  - `archived_log.csv`: Log all request with timestamp
    ```csv
    timestamp,type,url,status
    "910","Request","https://www.moha.gov.vn/","Sent"
    ```
  - `title_log.csv`: The real title of the page
  - `url_hash_log.csv`: Containing all signature that have been colected
  - `index.html`, `index_loaded.html`, `text_only_index_loaded.html.txt`: Page HTML data with 3 version
    - `text_only_index_loaded.html.txt`: Dynamic loadding page for 30s, but we only get `html.innerText` data
    - `index_loaded.html`: Dynamic loadding page for 30s, then we get full loaded html data
    - `index.html`: Static (page is not load) html file

    ![image](https://github.com/nghiango1/WebDefaceDetection/assets/31164703/f2bfe048-e9d9-4c89-bcd1-ec2de9b3f034)

> I don't have and will not provide any data that have been crawled and using for building the model here. It have been lost and can't be recovered, the file in saved directory was crawled recenterly just for example purpose. If you try repeated crawling and bypassing [zone-h.org](https://zone-h.org/) protected mechanism could lead to retricted and IP ban, please use the crawler with caution.

### Data preprocessing

n-gram frequency extraction
- HTML source code data standardized through the HTML crawler will be converted through a preprocessing step into feature vector form.
- After collecting a large enough amount as a profile, it is finally used as training data for a machine learning algorithm to build a classifier.

**Source**: `tf_caculation.py`

**Input**: `saved` directory
- Counting all 2-gram, 3-gram with each of these 3 `html-data` files `[text_only_index_loaded.html.txt, index_loaded.html, index.html]` apperence, chosing the top 300 n-gram with highest appearence
- Vectorize all page with each n-gram apearence in each page text file
**Output**: Example output is provided
- `n_gram_count`: Contain counting result from all set of input and config. `<n-gram><html-data>_count.csv`
- `tf_gram_count`: Contain vectorized page data using the top 300 `n-gram` of corespond `html-data` file
  - Each round in csv representing a page `html-data`
  - `i'th` column is the frequency of `i'th` n-gram in the top 300 appear in the page 

### Data modeling

Python Machine learning Framwork (sklearn, matplotlib, numpy), RandomForest, NaiveBayes classifier

**Source**: `model_and_measurement.py`

**Input**: Vectorized data - You can use Example file from `tf_gram_count`
**Output**: Result metric only - Example `0.25_final.csv`, `0.5_final.csv`
- Using RandomForest, NaiveBayes classifier for modeling the input data
- Model isn't save by default: New model will be train on the input on each run and only output the final result metric

### Result analysis

Using [confusion matrix](https://en.wikipedia.org/wiki/Confusion_matrix), I draw the conclusion base on 4 metric
- Accuracy: Overall accuracy of the model. `(TP+FN) / (TP+FP+TN+FN) × 100%`
- Percision: Accuracy of predicting the attacked sample. `TP / (TP+FP) ×100%`
- Recall: Ability to find all attacked samples of the model. `TP / (TP+FN) × 100%`
- Fail Alarm: False alarm rate. `FP / (FP+TN) ×100%`

There is only the result with 400 records ( 200 safe **Vietnamese** page - 200 deface page) in this repo from provided URL list file. 
- `0.25_final.csv` contain result of the model build with 75% data use for tranning and 25% data use for test
- `0.5_final.csv` contain result of the model build with 50% data use for tranning and 50% data use for test

But, the largest run of the thesis have 1600 records (with 800 safe **mix language** page - 800 Deface pages) with 50% traning - 50% testing, which conclude the thesis proposed model can gives good performance and have a very high accuracy rate.

| **Clasification Algorithm** | **File**          | **n-gram** | **percision**  | **recall** | **accuracy**              | **Fail Alarm** |
| --------------------------- | ----------------- | ---------- | -------------- | ---------- | ------------------------- | -------------- |
| RandomForest                | index.html        | 2          | 97.87%         | 97.87%     | 97.98%                    | 1.92%          |
| NaiveBayes                  | index.html        | 2          | 99.40%         | 88.27%     | 94.18%                    | 0.48%          |
| RandomForest                | index.html        | 3          | 98.93%         | 98.40%     | 98.74%                    | 0.96%          |
| NaiveBayes                  | index.html        | 3          | 98.82%         | 89.60%     | 94.56%                    | 0.96%          |
| RandomForest                | index_loaded.html | 2          | 96.40%         | 97.66%     | 97.13%                    | 3.37%          |
| NaiveBayes                  | index_loaded.html | 2          | 99.40%         | 86.98%     | 93.50%                    | 0.48%          |
| RandomForest                | index_loaded.html | 3          | 97.90%         | 97.14%     | 97.63%                    | 1.92%          |
| NaiveBayes                  | index_loaded.html | 3          | 99.41%         | 87.24%     | 93.63%                    | 0.48%          |
| RandomForest                | text_only.txt     | 2          | 95.94%         | 98.95%     | 97.49%                    | 3.86%          |
| NaiveBayes                  | text_only.txt     | 2          | 99.15%         | 91.88%     | 95.73%                    | 0.72%          |
| RandomForest                | text_only.txt     | 3          | 96.92%         | 98.95%     | 97.99%                    | 2.89%          |
| NaiveBayes                  | text_only.txt     | 3          | 97.55%         | 93.98%     | 95.98%                    | 2.17%          |
