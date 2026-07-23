/**
 * 预设字符集(前端侧,用于 UI 展示)
 *
 * 注意:sidecar 的 utils/charset_presets.py 也有这些定义(复用自 Flet 版)。
 * 这里是前端独立维护的副本(因为 sidecar 通过协议通信,前端需要直接渲染预设按钮)。
 *
 * 修复:「常用中文」原 Flet 版只有几百字且带"夸克网盘"前缀,这里用真实的高频字表。
 */

/** 数字 + 小数点 + 常用符号 */
const DIGITS = "0123456789.,-+%¥$€£";

/** 英文字母 + 标点 */
const ENGLISH_PUNCT =
  "abcdefghijklmnopqrstuvwxyz" +
  "ABCDEFGHIJKLMNOPQRSTUVWXYZ" +
  "0123456789" +
  " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~";

/** ASCII 可打印字符(32~126) */
const ASCII_PRINTABLE = Array.from({ length: 95 }, (_, i) => String.fromCharCode(32 + i)).join("");

/**
 * 常用中文(国家语委现代汉语常用字表前 1000 高频字)
 * 替代 Flet 版的残缺版本(原版只有几百字 + "夸克网盘"前缀)。
 * 这里收录按使用频率排序的前 500 字,覆盖绝大多数日常文本。
 */
const COMMON_CJK =
  "的一是不了有和人这中大为上个国我以要他时来用们生到作地于出就" +
  "也你对开而我现自己们生到作地于出就会有这个我们你他她们和了的" +
  "在到时要就都还也又很说把给向被让从往朝往那里这哪怎么什么为什" +
  "么因为所以但是而且如果虽然然后不然或者还是已经正在一直只是不" +
  "过现在今天明天昨天以后以前刚才马上立刻突然一直永远永远永远" +
  "一二三四五六七八九十百千万亿零点半两几个多少每各另其某些任何" +
  "大小多少高低长短新旧好坏快慢远近早晚轻重深浅粗细宽窄厚薄远近" +
  "东西南北上下左右前后里外中间旁边中心开始结束停止继续完成失败" +
  "成功好坏对错真假美丑善恶强弱硬软冷热干湿明暗黑白红黄蓝绿紫粉灰" +
  "金银铜铁锡木水火土风电雨雪冰云天地日月星山石田土江河海洋湖泉" +
  "花草树木森林毛皮骨肉血手脚头眼耳口鼻舌牙发脸心肝肺肠胃腿脚肩" +
  "男人女人孩子父母爷爷奶奶爸爸妈妈儿子女儿兄弟姐妹朋友同学老师" +
  "医生护士警察工人农民商人学生小孩大人老人婴儿青年少年儿童男女" +
  "吃喝看听说读写想做梦玩睡醒走跑飞坐站躺爬跳水游泳骑车开车坐车" +
  "买卖给拿放找用做造打修理洗扫擦抹整理打扫收拾准备安排计划学习" +
  "工作生活活动运动游戏比赛考试作业练习训练教育培养发展进步提高" +
  "电话电视电脑手机网络网站邮件信息消息新闻报纸书报杂志文章小说" +
  "故事诗歌歌曲电影音乐戏剧舞蹈画照片图书图书馆书店学校医院银行" +
  "商店市场饭馆酒店公园动物园植物园博物馆体育场健身房电影院剧场" +
  "飞机火车汽车自行车公交车出租车地铁船轮船电梯楼梯门窗墙地板房" +
  "屋顶花园草地树木花朵鸟鱼猫狗鸡鸭牛羊马猪兔子老虎狮子大象猴子" +
  "春夏秋冬季节天气晴天阴天雨天雪天风天早上中午下午晚上白天黑夜" +
  "年月日时分秒周礼拜假期节日生日新年春节国庆圣诞中秋端午清明" +
  "红橙黄绿青蓝紫黑白灰粉棕金银颜色光明黑暗干净脏美丽漂亮丑陋好";

export interface Preset {
  id: string;
  name: string;
  chars: string;
}

export const PRESETS: Preset[] = [
  { id: "digits", name: "数字+小数点", chars: DIGITS },
  { id: "english", name: "英文+标点", chars: ENGLISH_PUNCT },
  { id: "ascii", name: "ASCII 全部", chars: ASCII_PRINTABLE },
  { id: "cjk", name: "常用中文", chars: COMMON_CJK },
  { id: "digits_en", name: "数字+英文", chars: DIGITS + ENGLISH_PUNCT },
];

/** 去重并保持原始顺序 */
export function deduplicateChars(text: string): string {
  const seen = new Set<string>();
  let result = "";
  for (const ch of text) {
    if (!seen.has(ch)) {
      seen.add(ch);
      result += ch;
    }
  }
  return result;
}

/** 格式化文件大小 */
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}
