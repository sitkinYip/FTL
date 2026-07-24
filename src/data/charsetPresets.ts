/**
 * 预设字符集(前端侧,用于 UI 展示)
 *
 * 注意:sidecar 的 utils/charset_presets.py 也有这些定义(复用自 Flet 版)。
 * 这里是前端独立维护的副本(因为 sidecar 通过协议通信,前端需要直接渲染预设按钮)。
 *
 * 修复:「常用中文」原 Flet 版只有几百字且带"夸克网盘"前缀,
 * 这里用现代汉语常用字表(GB2312 一级)的高频字,运行时去重。
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
const ASCII_PRINTABLE = Array.from({ length: 95 }, (_, i) =>
  String.fromCharCode(32 + i)
).join("");

/**
 * 常用中文(现代汉语常用字表高频字)
 *
 * 替代 Flet 版的残缺版本(原版只有几百字 + "夸克网盘"前缀)。
 * 采用 GB2312 一级汉字中按使用频率排序的高频字,
 * 覆盖日常中文文本约 90%。源数据允许重复,由 deduplicateChars 去重。
 */
const COMMON_CJK_RAW =
  // 最高频功能词 + 代词 + 量词
  "的了一是在不有和人这中大为上个国我以要他时来用们生到作地于出会" +
  "可对也你就分而起着等被把给向从让里到要就都还也又很说只还再已正" +
  "过现么那哪怎什为因所此但其虽然或还已经正一直只些每各某另其任何" +
  // 数量
  "一二三四五六七八九十百千万亿零点半两几个多少每另些" +
  // 方位/空间/时间
  "东南西北上下左右前后里外中间旁中边心开结始停止继完成败失功" +
  "春夏秋冬今天明昨以后前刚才马上刻立突永年月日时分秒周礼拜假" +
  // 自然/物质
  "天地日月星山石田土江河海洋湖泉水火风雨雪冰云光电气" +
  "金木花草树林森毛皮骨肉血铜铁锡土沙泥" +
  // 颜色
  "黑白红黄蓝绿紫粉灰棕金银青橙颜色光明暗净脏丽漂亮陋美丑善恶" +
  // 人体/亲属/人物
  "手脚头眼耳口鼻舌牙发脸心肝肺肠胃腿脚肩男人女人孩子" +
  "父母爷奶爸妈儿子女儿兄弟姐妹朋友同学老师医生护士警察工人农民商人" +
  "学生小孩大人老婴幼青少男童" +
  // 动作
  "吃喝看听说读写想做梦玩睡醒走跑飞坐站躺爬游骑开买" +
  "卖拿放找用造打修理洗扫擦抹整收准备安排划学作活运动游戏" +
  // 认知/抽象
  "知道理路法意思想念头脑力智力感情知觉认识解释决" +
  "好坏对错真假强弱软硬冷热干湿粗细宽厚薄轻深浅高远近早晚快慢新" +
  // 社会/建筑/交通
  "城城市镇村街道路桥楼房房屋顶门窗墙板院校园场馆店商场" +
  "银行医院书店图书邮局站厂公园物园博物体育健身电影院剧场" +
  "飞火车自行公共汽出租地铁船轮电梯楼梯桌椅床灯钟表电视脑手机" +
  // 文具/文化
  "笔墨纸张书本报杂志文章说诗歌歌曲影音乐戏剧舞蹈画" +
  "照片文字词语言语谈话讨论问答题作业练习考比赛" +
  // 食物/衣物
  "饭菜汤水面米茶酒糖果盐油肉鱼鸡鸭牛羊猪蛋衣裤鞋帽" +
  // 生物
  "狗猫鸟兔鼠虎狮象猴鸡鸭鹅牛马羊猪" +
  // 程度/状态/其它高频
  "大小多少好坏新旧快慢轻重长短高低远近粗细宽厚深浅" +
  "满空完整破损打开始结束继续停完成功失败真假是非对错" +
  "容易困难简单复杂安全危险清洁脏干净";

export interface Preset {
  id: string;
  name: string;
  chars: string;
}

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

// 常用中文去重后使用
const COMMON_CJK = deduplicateChars(COMMON_CJK_RAW);

export const PRESETS: Preset[] = [
  { id: "digits", name: "数字+小数点", chars: DIGITS },
  { id: "english", name: "英文+标点", chars: ENGLISH_PUNCT },
  { id: "ascii", name: "ASCII 全部", chars: ASCII_PRINTABLE },
  { id: "cjk", name: "常用中文", chars: COMMON_CJK },
  { id: "digits_en", name: "数字+英文", chars: DIGITS + ENGLISH_PUNCT },
];

/** 格式化文件大小 */
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}
