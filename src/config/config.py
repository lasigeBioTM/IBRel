import json
import shutil


def main():
    with open("settings_base.json", "r") as settings:
        vals = json.load(settings)
        for k in vals:
            vals[k] = raw_input("{0}? (current: {1})".format(k, vals[k])) or vals[k]
    shutil.copy("bin/base.prop", vals["stanford_ner_dir"])
    with open("settings.json", "w") as settings:
        json.dump(vals, settings, sort_keys=True, indent=4)

if __name__ == "__main__":
    main()

with open("settings.json") as settings:
    vals = json.load(settings)
    use_chebi = vals["use_chebi"]
    if use_chebi:
        chebi_host = vals["chebi_host"]
        chebi_user = vals["chebi_user"]
        chebi_pw = vals["chebi_pw"]
        chebi_db = vals["chebi_db"]
    use_go = vals["use_go"]
    if use_go:
        go_host = vals["go_host"]
        go_user = vals["go_user"]
        go_pw = vals["go_pw"]
        go_db = vals["go_db"]
    host_ip = vals["host_ip"]
    geniass_path = vals["geniass_path"]
    florchebi_path = vals["florchebi_path"]
    corenlp_dir = vals["corenlp_dir"]
    stanford_ner_dir = vals["stanford_ner_dir"]
    stanford_ner_train_ram = vals["stanford_ner_train_ram"]
    stanford_ner_test_ram = vals["stanford_ner_test_ram"]
    stoplist = vals["stoplist"]
    mirbase_path = vals["mirbase_path"]

if use_chebi or use_go:
    import MySQLdb
if use_chebi:
    chebi_conn = MySQLdb.connect(host=chebi_host,
                                 user=chebi_user,
                                 passwd=chebi_pw,
                                 db=chebi_db)
if use_go:
    go_conn = MySQLdb.connect(host=go_host,
                              user=go_user,
                              passwd=go_pw,
                              db=go_db)

relation_types = {"miRNA-gene":
        {"source_role": "agent",
         "source_types": ("mirna"),
         "target_role": "target",
         "target_types": ("protein"),
         "event": "interaction",
         "keywords": ["bind", "ligand", "interact"]},}