import os

from agentscope.message import Msg
from agentscope.msghub import msghub
import agentscope
from agentscope.agents.user_agent import UserAgent
from agentscope.agents.dialog_agent import DialogAgent
from agentscope.agents.text_to_image_agent import TextToImageAgent
import gradio as gr
import requests
import concurrent.futures
from PIL import Image
import io


def get_weather():
    weather_key = '494d50b3bfe009cc5e0da51d25e6bff0'  # 每天50次调用额度, 尽量自己申请一个 https://dashboard.juhe.cn/data/index/my
    url = "http://apis.juhe.cn/simpleWeather/query"
    params = {
        'city': u'上海',
        'key': weather_key,
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data['error_code'] != 0:
        print('天气啊查询失败，原因：', data['reason'])
        return '未查询到当前天气'
    realtime_data = data['result']['realtime']
    realtime_str = '当前天气%s, 温度：%s℃, 湿度：%s%%, 风向：%s 风力：%s 空气质量：%s' % (
        realtime_data['info'], realtime_data['temperature'], realtime_data['humidity'], realtime_data['direct'],
        realtime_data['power'], realtime_data['aqi']
    )

    return realtime_str


weather = get_weather()
API_KEY = os.getenv('DASHSCOPE_API_KEY')

agentscope.init(
    model_configs=[
        {
            "config_name": "tongyi_chat1",
            "model_type": "dashscope_chat", "api_key": API_KEY,
            "model_name": "qwen-max"
        },
        {
            "config_name": "tongyi_chat2",
            "model_type": "dashscope_chat", "api_key": API_KEY,
            "model_name": "qwen-max-0428"
        },
        {
            "config_name": "tongyi_chat3",
            "model_type": "dashscope_chat", "api_key": API_KEY,
            "model_name": "qwen-max-0403"
        },
        {
            "config_name": "tongyi_chat4",
            "model_type": "dashscope_chat", "api_key": API_KEY,
            "model_name": "qwen-max-0107"
        },
        {
            "config_name": "tongyi_chat5",
            "model_type": "dashscope_chat", "api_key": API_KEY,
            "model_name": "qwen-max-1201"
        },
        {
            "config_name": "tongyi_image",
            "model_type": "dashscope_image_synthesis",
            "api_key": API_KEY,
            "model_name": "wanx-v1"
        }
    ]
    # agent_configs="./configs/agent_configs.json",
)

PM_prompt = '''
我们是一家为顾客提供穿衣方案的公司，你是负责人，我司有三个着装顾问：Consulter1、Consulter2、Consulter3，和一个人工智能驱动的穿搭肖像绘画师painter。
顾问的职责是按顾客需求（该需求在host的message中给出）提供一套穿搭建议，建议会以如下格式给出（[穿搭建议]标签内为示例）：
    [穿搭建议]
        上衣：选择一件白色宽松版型的棉质T恤，胸前可有一些绿色或黑色的小图案作为点缀，这样既可以满足您对色调的要求，又能通过宽松设计来平衡上半身比例。
        裤子：搭配一条深绿色或者军绿色的直筒休闲裤，面料可以选择棉麻混纺，透气性好且舒适，直筒设计可以修饰大腿偏粗的问题，同时避免紧身裤带来的束缚感。
        鞋子：鉴于您前脚掌较宽，建议选择一双黑色的New Balance或者Nike等品牌的运动休闲鞋，尺码为41码，这类鞋子通常有足够的前掌空间，穿着更加舒适。确保鞋子款式简洁大方，能与整体着装风格相协调。
        配件：可以佩戴一条黑色简约皮带，既能凸显腰围适中的优点，又能与整体色彩形成呼应。

为了避免歧义，应当每个部分有且仅有一种风格的推荐（如上衣：不能同时推荐白色T恤和其他颜色的上衣）。
你作为管理层负责如下内容：
1.把控他们的工作，在每一个顾问说出他们的建议后，会先交给你审核，审核他们的建议：
    （1）.是否符合上面的格式；
    （2）.是否满足推荐明确的要求。
    当他们的回复符合要求时，回复 yes,否则回复no，并给出相应的说明。
2.当顾问的回复符合需要时（即回复了yes时才做），你需要根据host中的需求和顾问的建议，给painter以明确的场景和人物、穿搭描述，以便他根据你的描述绘制写真。

具体的回复格式如下（首先判断yes和no,再选择对应的模板回复。
1. 顾问的回复满足要求时，模板为：
    yes
    天气：{天气}
    场景：{场景}
    人物特征：{人物特征}
    穿搭描述：{穿搭描述}

2. 顾问的回复不满足要求时，模板为：
    no
    原因：{原因说明}

'''

consulter_prompt = '''
我们是一家为顾客提供穿衣方案的公司，你是我司的着装顾问，你的职责是为顾客提出针对性的着装建议
host给出了顾客的要求，你的回复模板如下：
---
[穿搭建议]
    上衣：{给出一种上衣建议}
    裤子：{给出一种裤子建议}
    鞋子：{给出一种鞋子建议}
    配件：{给出配件建议}
---
为了避免歧义，应当每个部分有且仅有一种风格的推荐（如上衣：不能同时推荐白色T恤和其他颜色的上衣）。
请严格按照上面的模板给出你的建议。当你的建议没有按照模板回答，或是存在推荐不明确的问题时，PM会回复no，并给出相应的说明，你需要按照他给出的提示修改建议
'''

painters_prompt = '''
绘制人物画像
'''

host_prompt = '''
我们是一家为顾客提供穿衣方案的公司，需要根据需求为客户提供今日穿搭建议，以下是一些需要的信息：
1. 今天本地的天气：{}
2. 用户具体需求：{}
'''

PM = DialogAgent(
    name="PM",
    sys_prompt=PM_prompt,
    model_config_name="tongyi_chat",  # replace by your model config name
)

consulter1 = DialogAgent(
    name="Consulter1",
    sys_prompt=consulter_prompt,
    model_config_name="glm_chat",  # replace by your model config name
)

consulter2 = DialogAgent(
    name="Consulter2",
    sys_prompt=consulter_prompt,
    model_config_name="tongyi_chat2",  # replace by your model config name
)

consulter3 = DialogAgent(
    name="Consulter3",
    sys_prompt=consulter_prompt,
    model_config_name="baichuan_chat",  # replace by your model config name
)

painter1 = TextToImageAgent(
    name="Painter1",
    sys_prompt=consulter_prompt,
    model_config_name="tongyi_image",  # replace by your model config name
)

user = UserAgent(
    name="user",
)

final_advice = ""

def download_img_pil(index, img_url):
    # print(img_url)
    r = requests.get(img_url, stream=True)
    if r.status_code == 200:
        img = Image.open(io.BytesIO(r.content))
        return (index, img)
    else:
        gr.Error("图片下载失败!")
        return

def download_images(img_urls,batch_size):
    imgs_pil = [None] * batch_size
    # 下载单张图片
    if batch_size == 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            to_do = []
            future = executor.submit(download_img_pil, 1, img_urls)
            to_do.append(future)
            for future in concurrent.futures.as_completed(to_do):
                ret = future.result()
                # worker_results.append(ret)
                index, img_pil = ret
                imgs_pil[index-1] = img_pil 
        return img_pil
    
    else: # 下载多张图片放入gallert中
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            to_do = []
            for i, url in enumerate(img_urls):
                future = executor.submit(download_img_pil, i, url)
                to_do.append(future)

            for future in concurrent.futures.as_completed(to_do):
                ret = future.result()
                # worker_results.append(ret)
                index, img_pil = ret
                imgs_pil[index] = img_pil  # 按顺序排列url，后续下载关联的图片或者svg需要使用
        return imgs_pil

def dress_fn(user_requirement):
    gr.Markdown("请简要描述你的特征及场景：" + user_requirement)
    hint = Msg(
        name="Host",
        content=host_prompt.format(weather, user_requirement)  # user 描述示例 26岁男性，体型偏矮微胖，大腿稍粗，前脚略宽；今天去户外运动
    )
    actors = [PM, consulter1, consulter2, consulter3, painter1, user]
    with msghub(actors, announcement=hint):
        pass

    new_msg = Msg(name='', content="no")
    advices = []
    # for consulter in [consulter1, consulter2, consulter3]:
    for consulter in [consulter2]:
        round_count = 0
        while ('no' in new_msg.content or round_count == 0):
            new_msg = consulter()
            new_advice = new_msg.content
            new_msg = PM(new_msg)
            round_count += 1
            if round_count > 2:
                break  # 防止因幻觉导致的死循环
        if 'no' in new_msg.content:
            continue
        # img_res = painter1(new_msg)
        # display(IPython.display.Image(url=img_res.url[0]))
        advices.append({'advice': new_advice, 'advicer': consulter.name})

    if len(advices) == 0:
        print("推荐失败")
    print("final advice:", advices[0]['advice'])
    final_advice = advices[0]['advice'] + "\n"
    return final_advice

def generate_img(require,output):
    if len(require) == 0:
        raise gr.Error("人物特征不能为空")
        return

    tempt_text = require + output
    new_msg = Msg(name='', content=tempt_text)
    img_res = painter1(new_msg)
    img_data = download_images(img_res.url[0], len(img_res.url))
    return img_data

    


with gr.Blocks(css='style.css',theme=gr.themes.Soft()) as demo:
    with gr.Row():
        with gr.Column(scale=1):
            require = gr.Textbox(label="请简要描述你的特征及场景：", value="30岁男性，170cm，体重60kg，今天去户外运动")
            greet_btn = gr.Button("生成穿搭建议")
        # with gr.Column(scale=3):
            output = gr.Textbox(label="穿搭建议")
        with gr.Column():
            # result = gr.HTML(label='preview', show_label=True, elem_classes='preview_html')
            # result_image = gr.Gallery(
            #    label='preview', show_label=True, elem_classes="preview_imgs", preview=True, interactive=False)
            output_image = gr.Image()
            btn = gr.Button(value="生成穿搭画像", elem_classes='btn_gen')
            gr.Markdown("♨️ 图片较大，加载耗时，稍加等待~")
            # gr.Markdown("📌 鼠标右键保存到本地，或者在新标签页打开大图~")
    greet_btn.click(fn=dress_fn, inputs=require, outputs=output, api_name="dress_fn")
    btn.click(generate_img, inputs=[require,output],outputs=output_image)
    # new_msg = Msg(name='', content=output.value)
    # img_res = painter1(new_msg)
    # print("image", img_res)
    # gr.Image(value=img_res.url[0])

if __name__ == "__main__":
    demo.launch(share=True)
