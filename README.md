# BOC EUR/CNY 现汇卖出价爬虫（目前只支持每日手动运行）

这个小工具用于从中国银行「外汇牌价」页面抓取 **欧元（EUR）兑人民币（CNY）的现汇卖出价**，将结果 **追加保存到同一个 `.txt` 文件**，并可从该文件 **绘制汇率变化趋势图**。

> 说明：中行外汇牌价的报价单位通常是 **“100 外币兑换人民币”**。本项目会同时保存：
> - `spot_sell_100`：100 EUR 对应的 CNY
> - `spot_sell_1`：1 EUR 对应的 CNY（由 `spot_sell_100 / 100` 换算）
>
> 数据来源：https://www.boc.cn/sourcedb/whpj/

---

## 功能

- 抓取：欧元 **现汇卖出价**
- 存储：追加写入 `txt`（Tab 分隔，便于读取）
- 去重（可选）：同一个中行发布日（`boc_date`）默认不重复写入
- 可视化：读取 txt 并绘制趋势图（保存 png + 弹窗显示）

---

## 使用方法

### 1) 每日抓取一次并写入 txt (默认同日不重复写)

```bash
python boc_eur_sell_spot.py fetch --file boc_eur_spot.txt
```

### 2) 强制写入(即使同日已记录)
```bash
python boc_eur_sell_daily.py fetch --file boc_eur_spot_sell.txt --force
```

### 3) 绘制趋势图
```bash
python boc_eur_cny_spot.py plot --file boc_eur_cny_spot.txt --out trend.png
```

## 免责声明
本项目仅用于学习与个人使用。数据来源于公开网页，汇率/牌价以中国银行官方发布为准。请遵守数据来源网站的相关条款与规定。