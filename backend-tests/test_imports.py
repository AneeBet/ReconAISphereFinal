def test_app_module_imports():
    import app.main
    import app.core.config
    import app.core.dependencies
    import app.db.base
    import app.db.database
    import app.utils.password
    import app.utils.jwt
    import app.reconciliation.rule_engine
    import app.reconciliation.matching_engine
    import app.reconciliation.reconciliation_service
    import app.parser.normalizer
    import app.agents.common.json_parser
    import app.mappers.transaction_mapper
    import app.exceptions.handlers
    import app.middleware.logging

    assert app.main.health()["status"] == "healthy"
    assert app.core.dependencies.require_admin is not None
    assert app.db.base.Base is not None
    assert app.utils.password.hash_password
    assert app.utils.jwt.create_access_token
    assert app.reconciliation.rule_engine.RuleEngine
    assert app.reconciliation.matching_engine.MatchingEngine
    assert app.parser.normalizer.Normalizer
    assert app.agents.common.json_parser.JsonParser
    assert app.exceptions.handlers.register_exception_handlers
    assert app.middleware.logging.RequestLoggingMiddleware
