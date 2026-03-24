"""
智能体模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, Text, DateTime, Index
from app.extensions import Base


class AiAgent(Base):
    """
    智能体模型
    
    存储智能体的配置信息，包括名称、模型、工具等
    """
    __tablename__ = 'ai_agent'
    

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='编号')
    name = Column(String(64), nullable=True, comment='智能体名字')
    model_id = Column(BigInteger, nullable=True, comment='模型标识')
    first_sentence_pattern = Column(Integer, nullable=True, default=1, comment='首句模式')
    sort = Column(Integer, nullable=True, comment='排序')
    status = Column(String(1), nullable=True, default='0', comment='账号状态（0正常 1停用）')
    prologue = Column(String(255), nullable=True, default='', comment='开场白')
    end_reply = Column(String(255), nullable=True, default='', comment='结束语')
    idle_message = Column(String(255), nullable=True, default='', comment='空闲消息')
    system_prompt = Column(Text, nullable=True, comment='系统提示词')
    custom_parameters = Column(Text, nullable=True, comment='自定义参数')
    transcription_model_id = Column(BigInteger, nullable=True, comment='转录模型id（asrId）')
    transcription_language_id = Column(BigInteger, nullable=True, comment='转录语言id（asr语言Id）')
    convert_speech_language_id = Column(BigInteger, nullable=True, comment='转语音语言id（tts语言Id）')
    convert_speech_timbre_id = Column(BigInteger, nullable=True, comment='转语音音色id（tts音色Id）')
    temperature = Column(String(50), nullable=True, comment='温度参数')
    max_tokens = Column(Integer, nullable=True, comment='单条回复的最大 Token 数量')
    speech_wait = Column(String(50), nullable=True, default='0.5', comment='发言等待（0-2，每个0.1为一段）')
    react_mode = Column(Integer, nullable=True, default=1, comment='ReAct模式（0关闭 1开启）')
    knowledge_base = Column(Text, nullable=True, comment='知识库（JSON数组格式）')
    workflow = Column(Text, nullable=True, comment='工作流（JSON数组格式）')
    tools = Column(Text, nullable=True, comment='工具（JSON数组格式）')
    max_idle_message_count = Column(Integer, nullable=True, default=2, comment='最大空闲消息数')
    idle_message_interval = Column(String(50), nullable=True, default='2', comment='空闲消息发送间隔（秒）')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=False, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=False, comment='更新时间')
    description = Column(String(500), nullable=True, comment='描述')
    remark = Column(String(500), nullable=True, comment='备注')
    del_flag = Column(String(1), nullable=True, default='0', comment='删除标志（0代表存在 2代表删除）')
    
    __table_args__ = (
        {'comment': '智能体表'}
    )
    
    def __repr__(self):
        return f'<AiAgent {self.id}: {self.name}>'
