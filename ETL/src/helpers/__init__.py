from .geometry import parse_way, parse_relation, ensure_multipolygon
from .utils import get_super_type, build_overpass_query, build_routing_query, time_this_function
from .logs import init_logger, die, info, done

init_logger()