from collections import Counter
import json
import os
from pprint import pprint
import random

import IPython

POETRY_DATA_DIR = "./chinese-poetry-master/"
DATAS_CONFIG = "./data/poetry_manifest.json"


class PlainDataLoader():
    def __init__(self, config_path: str=DATAS_CONFIG) -> None:
        self._path = config_path
        with open(config_path, 'r', encoding='utf-8') as config:
            data = json.load(config)
            self.top_level_path:str = data["cp_path"]
            self.datasets:dict = data["datasets"]
            self.id_table = {
                v["id"]: k for (k, v) in self.datasets.items()
            }
    
    def body_extractor(self, target: str) -> list:
        if target not in self.datasets:
            print(f"{target} is not included in datas.json as a dataset")
            return None # type: ignore
        configs = self.datasets[target]
        tag = configs["tag"]
        body = []  # may get a bit huge... 
        full_path = POETRY_DATA_DIR + os.path.join(self.top_level_path, configs["path"])
        if os.path.isfile(full_path):  # single file json
            with open(full_path, mode='r', encoding='utf-8') as file:
                data = json.load(file)
                for poem in data:
                    body.append(poem)
            return body
        
        # a dir, probably with a skip list
        subpaths = os.listdir(full_path)
        for filename in subpaths:
            if "excludes" in configs and filename in configs["excludes"]:
                continue
            with open(os.path.join(full_path, filename), mode='r', encoding='utf-8') as file:
                data = json.load(file)
                for poem in data:
                    body.append(poem)
        return body

    def extract_from_multiple(self, targets: list) -> list:
        results = []
        for target in targets:
            results += self.body_extractor(target)
        return results
    
    def extract_with_ids(self, ids: list) -> list:
        results = []
        for id in ids:
            results += self.body_extractor(
                self.id_table[id]
            )
        return results



if __name__ == "__main__":

    if not os.path.exists(POETRY_DATA_DIR):
        print(
            f"需要先下载中文诗歌数据集到 {POETRY_DATA_DIR} 目录下。\n"
            f"git clone https://github.com/chinese-poetry/chinese-poetry.git\n"
        )
        exit(1)

    loader = PlainDataLoader()
    cfg = json.load(open(DATAS_CONFIG))

    # all_poetrys = loader.extract_from_multiple(list(cfg['datasets'].keys()))
    # print(f"共计 {len(all_poetrys)} 首诗歌。")
    # while True:
    #     input()
    #     pprint(random.choice(all_poetrys))

    shijing = loader.body_extractor("shijing")
    for sj in shijing:
        sj['author'] = sj['chapter'] + '-' + sj['section']
        sj['type'] = '诗经'
    shuimotangshi = loader.body_extractor("shuimotangshi")
    for smts in shuimotangshi:
        smts['type'] = '水墨唐诗'
        smts['content'] = smts['paragraphs']
        del smts['paragraphs']
    nalanxingde = loader.body_extractor("nalanxingde")
    for nxd in nalanxingde:
        nxd['type'] = '纳兰性德'
        nxd['content'] = nxd['para']
        del nxd['para']
    songci = json.load(open(POETRY_DATA_DIR + '/宋词/宋词三百首.json'))
    for sc in songci:
        sc['type'] = '宋词'
        sc['title'] = sc['rhythmic']
        sc['content'] = sc['paragraphs']
        del sc['paragraphs']

    all_poetrys = shijing + shuimotangshi + random.choices(nalanxingde, k=100) + songci
    all_poetrys = [poem for poem in all_poetrys if len(''.join(poem['content'])) <= 60]
    all_poetrys = [poem for poem in all_poetrys if max([len(e) for e in poem['content']]) <= 20]

    print(f"共计 {len(all_poetrys)} 首诗歌。")
    print(Counter(poem['type'] for poem in all_poetrys))
    json.dump(
        all_poetrys,
        open("./data/shici.json", "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=2
    )
