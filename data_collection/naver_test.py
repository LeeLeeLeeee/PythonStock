from naver_sise_get import NaverSise


code = ["000020"]

naver = NaverSise()
for x in code:
    naver.set_code(x)
    naver.file_check()
    print(naver.get_all_value())
