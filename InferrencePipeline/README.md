- Step1. 基于原始模型，原始特征处理，调用sft版ChatGLM3, 生成label -> 类别。
- Step2. 基于该类别，Query换入对应类别的Prompt。查询类Query的用difflib需召回对应的前50,附在Query后。
- Step3. GLM4-9b模型调用, 生成思维链答案
- Step4. 从答案中解析最终的json答案