from dataclasses import dataclass
from typing import Dict, Any, Optional
import json


@dataclass
class LogoInfo:
    desktop_image: str
    mobile_image: str


@dataclass
class Header:
    id: int
    title: str
    description: str
    theme_color: str
    icon: str


@dataclass
class Website:
    uuid: str
    website_type: str
    name: str
    title: str
    logo: LogoInfo
    appbar: Dict[str, Any]  # Store as raw JSON (dict)
    header: Header
    open_graph: Optional[Any]
    theme: Dict[str, Any]  # Store as raw JSON (dict)
    has_login_with_google: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Website':
        """Create a Website instance from a dictionary."""
        # Process logo
        logo = LogoInfo(
            desktop_image=data['logo']['desktop_image'],
            mobile_image=data['logo']['mobile_image']
        )

        # Process header
        header = Header(
            id=data['header']['id'],
            title=data['header']['title'],
            description=data['header']['description'],
            theme_color=data['header']['theme_color'],
            icon=data['header']['icon']
        )

        # Create and return the Website instance
        return cls(
            uuid=data['uuid'],
            website_type=data['website_type'],
            name=data['name'],
            title=data['title'],
            logo=logo,
            appbar=data['appbar'],  # Store appbar as is (JSON/dict)
            header=header,
            open_graph=data['open_graph'],
            theme=data['theme'],  # Store theme as is (JSON/dict)
            has_login_with_google=data['has_login_with_google']
        )

    def to_json(self) -> str:
        """Convert the Website object to a JSON string."""
        # Create a dictionary representation
        website_dict = {
            'uuid': self.uuid,
            'website_type': self.website_type,
            'name': self.name,
            'title': self.title,
            'logo': {
                'desktop_image': self.logo.desktop_image,
                'mobile_image': self.logo.mobile_image
            },
            'appbar': self.appbar,
            'header': {
                'id': self.header.id,
                'title': self.header.title,
                'description': self.header.description,
                'theme_color': self.header.theme_color,
                'icon': self.header.icon
            },
            'open_graph': self.open_graph,
            'theme': self.theme,
            'has_login_with_google': self.has_login_with_google
        }
        # Convert to JSON string
        return json.dumps(website_dict)
