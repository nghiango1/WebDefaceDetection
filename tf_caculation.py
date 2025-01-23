import os
from typing import List, Dict
import csv

N_GRAM_SAVED_PATH = "n_gram_count/"
TF_SAVED_PATH = "tf_para_top_300/"
FORCE_RECOUNT = False


# As `saved` output directory from `archive_page.js` crawler store each page
# in seperated dir, this function return all child path in `saved` to a list
def get_valid_path(pages_saved_path=""):
    pages_saved_path = os.path.abspath(pages_saved_path)
    valid_path = filter(
        os.path.isdir,
        [os.path.join(pages_saved_path, x) for x in os.listdir(pages_saved_path)],
    )
    return list(valid_path)


# Helper for debug, try to get url name when there error preprocessing a pages
# As `archived_log.csv` contain the timespampt of every request, by skiping the
# csv header row, we get row_1['url'] mean the first url being request, aka the
# page url
def get_url(path):
    file_path = get_file(path, "archived_log.csv")
    if file_path is None:
        print('Error no "archived_log.csv"', path)
        return None
    f_input = open(file_path, "r", encoding="utf-8")
    reader = csv.DictReader(f_input)
    row_1 = reader.__next__()
    return row_1["url"]


# Helper to check if a file exist, return it path if it exist
def get_file(path, name):
    if not os.path.isdir(path):
        return None
    if os.path.exists(os.path.join(path, name)):
        return os.path.join(path, name)


def n_gram_counting(valid_path: List[str], fileName, n_gram) -> Dict[str, int]:
    all_file_path = list(
        filter(os.path.exists, [os.path.join(path, fileName) for path in valid_path])
    )
    result = {}
    for path in all_file_path:
        try:
            f_input = open(path, "r", encoding="utf-8")
            string = f_input.read()
        except Exception as e:
            print("	|", path, e)
            continue

        for i in [string[i: i + n_gram] for i in range(0, len(string) - n_gram)]:
            if i in result:
                result[i] += 1
            else:
                result[i] = 1
    return result


# Vectorized all pages with a n-gram list reference
def tf_caculate(valid_path, fileName, n, n_gram_lists):
    all_file_path = list(
        filter(os.path.exists, [os.path.join(path, fileName) for path in valid_path])
    )
    result = []
    for path in all_file_path:
        try:
            f_input = open(path, "r", encoding="utf-8")
            string = f_input.read()
        except Exception as e:
            print("	|", path, e)
            print("		|", get_url(path))
            continue
        tf, max = tf_caculate_string(string, n, n_gram_lists)
        if max != 0:
            tf = [i / max for i in tf]
            result += [tf]
    return result


# Return a vectorized representation of a string with a n-gram list reference
def tf_caculate_string(string, n, n_gram_lists):
    result = [0] * len(n_gram_lists)
    max = 0
    for n_gram in [string[i: i + n] for i in range(0, len(string) - n)]:
        if n_gram in n_gram_lists:
            i = n_gram_lists.index(n_gram)
            result[i] += 1
            if result[i] > max:
                max = result[i]
    return result, max


# Saving n-gram counting result
def save_n_gram_count(sorted_count_result, n_gram, filename):
    global N_GRAM_SAVED_PATH

    count_file_path = os.path.join(
        N_GRAM_SAVED_PATH, "_".join([filename, str(n_gram), "gram", "count.csv"])
    )
    count_file = open(count_file_path, "w", encoding="utf-8")
    N_GRAM_COUNT_FILE_writer = csv.writer(count_file, "unix")
    for i in sorted_count_result:
        N_GRAM_COUNT_FILE_writer.writerow([i[0], i[1]])
    count_file.close()


# Saving pages tf vectorize result
def save_n_gram_tf(rows, label, n_gram, filename, mode="w"):
    global TF_SAVED_PATH

    if rows.__len__() != label.__len__():
        return None
    saved_path = os.path.join(
        TF_SAVED_PATH, "_".join([filename, str(n_gram), "gram", "tf.csv"])
    )
    curr_file = open(saved_path, mode, encoding="utf-8")
    csv_writer = csv.writer(curr_file, "unix")
    for i in range(rows.__len__()):
        csv_writer.writerow(rows[i] + [label[i]])
    curr_file.close()


# Reading n-gram count result
def open_n_gram_count(n_gram, filename):
    global N_GRAM_SAVED_PATH

    curr_file_path = os.path.join(
        N_GRAM_SAVED_PATH, "_".join([filename, str(n_gram), "gram", "count.csv"])
    )
    if os.path.exists(curr_file_path):
        result = []
        count_file = open(curr_file_path, "r", encoding="utf-8")
        csv_reader = csv.reader(count_file, "unix")
        for row in csv_reader:
            result += [row[0]]
        count_file.close()
        return result
    return None


# Counting n-gram in all pages
def run_n_gram_count(
    n_gram,
    filename,
    safe_pages_path: List[str],
    deface_pages_path: List[str],
) -> List[str]:
    pages_path: List[str] = safe_pages_path + deface_pages_path

    # `n_gram_counting` return as dict, we change it to list for sorting
    n_gram_count_all = n_gram_counting(pages_path, filename, n_gram).items()
    n_gram_count_all_sorted = sorted(n_gram_count_all, key=lambda x: x[1], reverse=True)

    save_n_gram_count(n_gram_count_all_sorted, n_gram, filename)

    return [cols[0] for cols in n_gram_count_all_sorted]


# Preprocessing with each scenario of <n-gram><html-data> pair, save the final
# preprocessing result vectorize data for modeling step
def run(n_gram, filename, safe_pages_path, deface_pages_path):
    global FORCE_RECOUNT

    print("_".join([filename, str(n_gram), "gram", "count.csv"]))

    # Check if already done n-gram count, if not, start counting and
    # save result to file. FORCE_RECOUNT can be set to True to enforce
    # this to be alway run instead
    n_gram_lists = open_n_gram_count(n_gram, filename)
    if n_gram_lists is None or FORCE_RECOUNT:
        n_gram_lists = run_n_gram_count(
            n_gram, filename, safe_pages_path, deface_pages_path
        )

    n_gram_lists = n_gram_lists[:300]

    safe_tf = tf_caculate(safe_pages_path, filename, n_gram, n_gram_lists)
    label = [0] * safe_tf.__len__()
    save_n_gram_tf(safe_tf, label, n_gram, filename, "w")
    deface_tf = tf_caculate(deface_pages_path, filename, n_gram, n_gram_lists)
    label = [1] * deface_tf.__len__()
    save_n_gram_tf(deface_tf, label, n_gram, filename, "a")


def main():
    global TF_SAVED_PATH, N_GRAM_SAVED_PATH, FORCE_RECOUNT

    TF_SAVED_PATH = os.path.abspath(TF_SAVED_PATH)
    N_GRAM_SAVED_PATH = os.path.abspath(N_GRAM_SAVED_PATH)

    os.makedirs(TF_SAVED_PATH, exist_ok=True)
    os.makedirs(N_GRAM_SAVED_PATH, exist_ok=True)

    # Example only - safe and deface page should be save in different directory
    safe_pages_path = get_valid_path("saved/")

    # Example only - safe and deface page should be save in different directory
    deface_pages_path = get_valid_path("saved/")

    fileNames = ["text_only_index_loaded.html.txt", "index_loaded.html", "index.html"]
    n_gram_tests = [2, 3]

    # Try every scenario
    for n_gram in n_gram_tests:
        for filename in fileNames:
            run(n_gram, filename, safe_pages_path, deface_pages_path)


if __name__ == "__main__":
    main()
