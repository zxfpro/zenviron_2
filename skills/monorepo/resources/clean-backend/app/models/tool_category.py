"""
工具分类/工具集合模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, Index, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import Base
from app.utils.datetime_utils import get_beijing_time



tool_category_association = Table(
    'tool_category_associations',
    Base.metadata,
    Column('tool_id', Integer, ForeignKey('tools.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('tool_categories.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, nullable=False, default=get_beijing_time, comment='关联创建时间')
)


class ToolCategory(Base):
    """
    工具分类/工具集合模型
    
    用于对工具进行分组管理，一个分类可以包含多个工具
    """
    __tablename__ = 'tool_categories'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='分类ID')
    name = Column(String(50), nullable=False, unique=True, index=True, comment='分类名称（唯一）')
    description = Column(String(200), nullable=True, comment='分类描述')
    icon = Column(String(255), nullable=True, comment='分类图标URL')
    status = Column(
        Enum('enabled', 'disabled', name='category_status'),
        nullable=False,
        default='enabled',
        index=True,
        comment='分类状态: enabled-启用, disabled-停用'
    )
    sort_order = Column(Integer, nullable=False, default=0, comment='排序顺序（数字越小越靠前）')
    creator = Column(String(50), nullable=True, comment='创建人')
    created_at = Column(DateTime, nullable=False, default=get_beijing_time, comment='创建时间（北京时间）')
    updated_at = Column(
        DateTime,
        nullable=False,
        default=get_beijing_time,
        onupdate=get_beijing_time,
        comment='更新时间（北京时间）'
    )
    tools = relationship(
        'Tool',
        secondary=tool_category_association,
        back_populates='categories',
        lazy='dynamic'
    )

    __table_args__ = (
        Index('idx_category_status_sort', 'status', 'sort_order'),
        {'comment': '工具分类表'}
    )
    
    def to_dict(self):
        """
        转换为字典
        
        Returns:
            字典格式的分类信息（不包含工具列表，工具列表由API层处理）
        """
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'status': self.status,
            'sort_order': self.sort_order,
            'creator': self.creator,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
        
        return data
    
    def is_enabled(self):
        """判断分类是否启用"""
        return self.status == 'enabled'
    
    def enable(self):
        """启用分类"""
        self.status = 'enabled'
    
    def disable(self):
        """停用分类"""
        self.status = 'disabled'
    
    def __repr__(self):
        return f'<ToolCategory {self.id}: {self.name} ({self.status})>'

