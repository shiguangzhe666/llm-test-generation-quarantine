from typing import Callable, Union, Optional
import typing as t

T_template_filter = Callable[[str], str]
T_template_test = Callable[[str], bool]
T_template_global = Callable[[], object]
T_before_request = Callable[[], None]
T_after_request = Callable[[], None]
T_teardown = Callable[[], None]
T_template_context_processor = Callable[[], dict]
T_error_handler = Callable[[Exception], None]
T_url_value_preprocessor = Callable[[str], str]
T_url_defaults = Callable[[], None]


class BlueprintSetupState:
    def __init__(self, app: Optional[object] = None) -> None:
        self.app = app

    def record(self, f: Callable[[], None]) -> None:
        if self.app is not None:
            f(self)

    def record_once(self, f: Callable[[], None]) -> None:
        if self.app is not None:
            f(self)
            self.app = None

    @setupmethod
    def route(self, path: str, **options: dict) -> None:
        def decorator(f: Callable[[], None]) -> None:
            self.record(lambda s: s.app.add_url_rule(path, f.__name__, f, **options))
            return f

        return decorator

    @setupmethod
    def app_template_filter(
        self, name: Optional[str] = None
    ) -> Callable[[T_template_filter], T_template_filter]:
        def decorator(f: T_template_filter) -> T_template_filter:
            self.add_app_template_filter(f, name=name)
            return f

        return decorator

    @setupmethod
    def add_app_template_filter(
        self, f: T_template_filter, name: Optional[str] = None
    ) -> None:
        def register_template(state: BlueprintSetupState) -> None:
            state.app.jinja_env.filters[name or f.__name__] = f

        self.record_once(register_template)

    @setupmethod
    def app_template_test(
        self, name: Optional[str] = None
    ) -> Callable[[T_template_test], T_template_test]:
        def decorator(f: T_template_test) -> T_template_test:
            self.add_app_template_test(f, name=name)
            return f

        return decorator

    @setupmethod
    def add_app_template_test(
        self, f: T_template_test, name: Optional[str] = None
    ) -> None:
        def register_template(state: BlueprintSetupState) -> None:
            state.app.jinja_env.tests[name or f.__name__] = f

        self.record_once(register_template)

    @setupmethod
    def app_template_global(
        self, name: Optional[str] = None
    ) -> Callable[[T_template_global], T_template_global]:
        def decorator(f: T_template_global) -> T_template_global:
            self.add_app_template_global(f, name=name)
            return f

        return decorator

    @setupmethod
    def add_app_template_global(
        self, f: T_template_global, name: Optional[str] = None
    ) -> None:
        def register_template(state: BlueprintSetupState) -> None:
            state.app.jinja_env.globals[name or f.__name__] = f

        self.record_once(register_template)

    @setupmethod
    def before_app_request(self, f: T_before_request) -> T_before_request:
        self.record_once(
            lambda s: s.app.before_request_funcs.setdefault(None, []).append(f)
        )
        return f

    @setupmethod
    def after_app_request(self, f: T_after_request) -> T_after_request:
        self.record_once(
            lambda s: s.app.after_request_funcs.setdefault(None, []).append(f)
        )
        return f

    @setupmethod
    def teardown_app_request(self, f: T_teardown) -> T_teardown:
        self.record_once(
            lambda s: s.app.teardown_request_funcs.setdefault(None, []).append(f)
        )
        return f

    @setupmethod
    def app_context_processor(
        self, f: T_template_context_processor
    ) -> T_template_context_processor:
        self.record_once(
            lambda s: s.app.template_context_processors.setdefault(None, []).append(f)
        )
        return f

    @setupmethod
    def app_errorhandler(
        self, code: Union[type, int]
    ) -> Callable[[T_error_handler], T_error_handler]:
        def decorator(f: T_error_handler) -> T_error_handler:
            self.record_once(lambda s: s.app.errorhandler(code)(f))
            return f

        return decorator

    @setupmethod
    def app_url_value_preprocessor(
        self, f: T_url_value_preprocessor
    ) -> T_url_value_preprocessor:
        self.record_once(
            lambda s: s.app.url_value_preprocessors.setdefault(None, []).append(f)
        )
        return f

    @setupmethod
    def app_url_defaults(self, f: T_url_defaults) -> T_url_defaults:
        self.record_once(
            lambda s: s.app.url_default_functions.setdefault(None, []).append(f)
        )
        return f