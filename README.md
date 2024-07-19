## 插件说明
COW 插件
基于 Coze 的多模态封装插件，目前仅支持图片的处理。

# 插件安装
微信对话框中输入
```sh
#installp https://github.com/wangxyd/nicecoze.git
#scanp
```
也可直接将文件 所有文件 复制到 `plugins/coze_wrapper` 目录下。

## 插件配置

将 `plugins/coze_wrapper` 目录下的 `config.json.template` 配置模板复制为 `config.json`。
配合Coze里配置的各类图片插件来开启相应的开关和使用。

以下是插件配置项说明：

```bash
{
    "summary_image": { # 图片总结
        "enabled": true, 
        "instruct":"$总结内容",
        "prompt": "总结这张图中的内容",
    },
    "solve_problem": { # 图片解题
        "enabled": true,
        "instruct":"$解答习题",
        "prompt": "解答这张图中的习题",
    },
    "redraw_image": { # 图片重绘
        "enabled": true,
        "instruct":"$重绘风格",
        "prompt": "重绘这张图",
    },
    "finetune_image": { # 微调图片
        "enabled": true,
        "instruct":"$微调内容",
        "prompt": "微调这张图",
    },
    "analysis_image": { # 分析图片
        "enabled": true,
        "instruct":"$分析数据",
        "prompt": "分析这张图中数据",
    },
}

```
## 插件使用
1. 当在微信中发送图片后，会显示上传状态。
2. 当上传完成后会根据配置里的功能开关提示用户能使用相应的功能和图片的id。
3. 复制那一行文字，在对话中发送，即可启动相应的功能。

比如：
上传完成后，显示：
```bash
已完成上传，你想对图片做何操作：
$总结内容:135678932
$解答习题:135678932
$重绘风格:135678932:<你选择的风格>
$微调内容:135678932:<你微调的内容>
$分析数据:135678932

```

如果你想总结这张图片，请发送：
$总结内容:135678932

如果你想用梵高的方式重绘这张图片，请发送：
$重绘风格:135678932:梵高风格
