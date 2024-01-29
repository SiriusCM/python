list0 = ['邢碧旗', '碧旗', '邢紫萱', '紫萱', '索儿', '陆姐', '琪儿', '燕洁', '伟', '阿艺']
list1 = ['张艺萱', '艺萱', '鹿怡', '鹿怡', '许鑫', '李懂', '王琪', '段岩', '曹皛', '陈昶佳']

for index in range(1, 10):
    name = 'chap_0' + str(index) + '.txt'
    file0 = open('E://zyx/' + name, 'r', encoding='utf-8')
    file1 = open('E://' + name, 'w', encoding='utf-8')
    for s in file0.readlines():
        for i in range(0, len(list0)):
            s = s.replace(list0[i], list1[i])
        file1.write(s)
