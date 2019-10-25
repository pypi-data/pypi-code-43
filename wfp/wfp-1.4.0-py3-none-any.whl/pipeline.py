import os
import json
import kfp
import kfp.dsl as dsl
import uuid
import logging
from kfp import compiler
from .error import LoopError


app_log = logging.getLogger("wfp")


def get_node_by_name(nodes, name):
    """
    Args:
        nodes:
        name:

    Returns:

    """
    for node in nodes:
        if node.name == name:
            return node
    return None


def dag_root(nodes_dependencies):
    root_nodes = []
    for node, dependencies in nodes_dependencies.items():
        if not dependencies:
            root_nodes.append(node)
    return root_nodes


def dag_sort(nodes):
    """
    Args:
        nodes: 实验的所有节点

    Returns:
        从根节点到叶子节点的排序，排序后的列表中保证了被依赖的节点一定在该节点的前面。
    """

    # 计算所有node的依赖关系
    nodes_dependencies = {}
    for node in nodes:
        nodes_dependencies[node.name] = []
        for arg in node.inputs:
            if arg.HasField("upstream_node_output"):
                depend_node = arg.upstream_node_output.node_name
                if depend_node not in nodes_dependencies[node.name]:
                    nodes_dependencies[node.name].append(depend_node)

    # 排序后的节点，排序后
    sorted_nodes = []
    while nodes_dependencies:
        # find new root from nodes_dependencies
        root_nodes = dag_root(nodes_dependencies)
        # root node not found
        if not root_nodes:
            raise LoopError('Loop found in DAG')

        # remove found root from nodes_dependencies
        for node in root_nodes:
            nodes_dependencies.pop(node)
            sorted_nodes.append(get_node_by_name(nodes, node))

        # update nodes_dependencies
        for dependencies in nodes_dependencies.values():
            for node in root_nodes:
                if node in dependencies:
                    dependencies.remove(node)

    return sorted_nodes


def build_pipeline(pipeline_name, pipeline_description, nodes):
    """
    Args:
        pipeline_name: 实验名称
        pipeline_description: 实验描述
        nodes: 实验各节点

    Returns:
        构建实验DAG的装饰函数_decorator

    """
    # Pipeline的定义
    @dsl.pipeline(
        name=pipeline_name,
        description=pipeline_description)
    def _decorator():
        sorted_nodes = dag_sort(nodes)

        nodes_objects = {}
        for node in sorted_nodes:
            # build ContainerOp arguments
            node_args = []
            for arg in node.inputs:
                node_args.append('--%s' % arg.name)
                if arg.HasField("value"):
                    node_args.append(arg.value)
                elif arg.HasField("upstream_node_output"):
                    node_output = arg.upstream_node_output
                    node_args.append(
                        nodes_objects[node_output.node_name].outputs[node_output.output_name])

            # build ContainerOp outputs
            node_outputs = {}
            output_args = []
            for item in node.outputs:
                '''
                每个item的message结构如下：
                message {
                    string name = 1;
                    DataType type = 2;
                    string uri = 3;
                }
                '''
                # 构造一个metapath
                node_outputs[item.name] = "/tmp/%s" % str(uuid.uuid4())
                output_args.append({
                    "name": item.name,
                    "type": item.type,
                    "uri": item.uri,
                    "metapath": node_outputs[item.name]
                })

            node_args.append("--output")
            node_args.append(json.dumps(output_args))

            '''
            ContainerOp structure as following:
            
            dsl.ContainerOp(
                name='hello',
                image='hello:v1',
                argument=[
                    '--arg1', 'tb_data1',  # 普通参数
                    '--arg2', {'PipelineParam': {'op_name': 'preprocess', 'name': 'data', 'value': None}},  # 上游节点输出
                    '--output', '[{"name": "model", "type": 12, "uri": "~/mnist_model", "metapath": "/tmp/fa05560d-a9db-4813-ab12-8e412e4983fc"}]'
                ],
                file_outputs={
                    # myfile的内容为model文件的元数据信息，元数据信息包括：
                    # {"name": "model", "type": 12, "uri": "~/mnist_model"}
                    'model': '/tmp/fa05560d-a9db-4813-ab12-8e412e4983fc'  
                }
            )
            '''
            # build ContainerOp object and save it into nodemap dict
            nodes_objects[node.name] = dsl.ContainerOp(
                name=node.name,
                image=node.image,
                command=node.command,
                arguments=node_args,
                file_outputs=node_outputs)

            # 设置cpu限制
            if node.cpu_limit:
                nodes_objects[node.name].set_cpu_limit(node.cpu_limit)
            # 设置gpu限制
            if node.gpu_limit:
                nodes_objects[node.name].set_gpu_limit(node.gpu_limit)
            # 设置内存限制
            if node.mem_limit:
                nodes_objects[node.name].set_memory_limit(node.mem_limit)

            # 设置环境变量
            for env in node.env_variables:
                nodes_objects[node.name].add_env_variable({'name': env.name, 'value': env.value})

            # 设置node selector
            nodes_objects[node.name].add_node_selector_constraint('hub.jupyter.org/node-purpose', 'user')

    return _decorator


def compile_pipeline(pipeline_name, pipeline_description, job_name, nodes):
    """
    Args:
        pipeline_name: 实验的名称
        pipeline_description: 实验的描述
        job_name: 实验任务名称
        nodes: 实验中的节点

    Returns:
        实验任务编译后的package

    """
    # Compile it into a tar package.
    job_package = '/tmp/%s_%s.tar.gz' % (pipeline_name, job_name)
    compiler.Compiler().compile(
        build_pipeline(pipeline_name, pipeline_description, nodes), job_package)

    return job_package


def run_pipeline(pipeline_name, pipeline_description, job_name, nodes):
    """
    Args:
        pipeline_name: 实验的名称
        pipeline_description: 实验的描述
        job_name: 实验任务名称
        nodes: 实验中的节点

    Returns:
        实验任务的id

    """
    client = kfp.Client()

    # 获取实验的ID
    try:
        exp = client.get_experiment(experiment_name=pipeline_name)
    except Exception as e:
        app_log.info("Experiment '%s' not found, will create it automatically")
        exp = client.create_experiment(pipeline_name)

    # 在该实验下运行job
    job_package = compile_pipeline(pipeline_name, pipeline_description, job_name, nodes)
    run = client.run_pipeline(exp.id, job_name, job_package)

    # 清理实验的pipeline临时文件
    if os.path.exists(job_package):
        os.remove(job_package)

    return run.id, exp.id


def get_pipeline_status(job_id):
    """
    Args:
        job_id: 实验中的节点

    Returns:
        实验任务状态和各节点的状态

    """
    job = kfp.Client().get_run(job_id)
    workflow = json.loads(job.pipeline_runtime.workflow_manifest)
    return workflow


def delete_experiment(id):
    """
    Args:
        id: 实验的id

    Returns:
        返回为空
    """
    client = kfp.Client()
    client._experiment_api.delete_experiment(id)


def delete_job(id):
    """
    Args:
        id: 作业的id

    Returns:
        返回为空

    """
    client = kfp.Client()
    client._run_api.delete_run(id)
