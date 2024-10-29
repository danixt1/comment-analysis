from behave import *
import src.datasets.helper as helper
textdata="""# message
{}
# type
{}
# behavior
{}
# spam It should NOT interfere in the test
{}
# problems
{}
# comment
{}
 """
@given("content to insert in dataset")
def step_impl(ctx):
    row = ctx.table[0]
    ctx.sample_text = textdata.format(row["message"],row["type"],row["behavior"],row["spam"],row["problems"],row["comment"])
    print("result "+ctx.sample_text)
@when("dataset helper receive the text")
def step_impl(ctx):
    ctx.data =helper.extractDataFrom(ctx.sample_text)

@then("data is returned without none in value")   
def step_impl(ctx):
    assert all(not x == None for x in ctx.data.values())