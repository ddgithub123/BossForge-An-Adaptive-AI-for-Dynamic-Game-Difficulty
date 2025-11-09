import os, re, shutil

def backup_cns(cns_path):
    bak = cns_path + ".bak"
    if not os.path.exists(bak):
        shutil.copy(cns_path, bak)

def read_params(cns_path):
    txt = open(cns_path, "r", encoding="utf-8").read()
    m1 = re.search(r'var\(50\)\s*=\s*([0-9]*\.?[0-9]+)', txt)
    m2 = re.search(r'var\(51\)\s*=\s*([0-9]*\.?[0-9]+)', txt)
    return (float(m1.group(1)), float(m2.group(1))) if m1 and m2 else (0.5, 1.0)

def write_params(cns_path, aggression, reaction):
    backup_cns(cns_path)
    s = open(cns_path, "r", encoding="utf-8").read()
    s = re.sub(r'var\(50\)\s*=\s*[0-9]*\.?[0-9]+', f'var(50) = {aggression}', s)
    s = re.sub(r'var\(51\)\s*=\s*[0-9]*\.?[0-9]+', f'var(51) = {reaction}', s)
    open(cns_path, "w", encoding="utf-8").write(s)
    print(f"[cns] wrote aggression={aggression:.3f}, reaction={reaction:.3f}")
