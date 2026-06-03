import argparse
import logging
import os
import sys

import pandas as pd


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )


def resolve_path(path: str) -> str:
    if os.path.isabs(path):
        return path
    cwd_path = os.path.abspath(path)
    if os.path.exists(cwd_path):
        return cwd_path

    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, path)


def carregar_dados(csv_filename: str) -> pd.DataFrame:
    csv_path = resolve_path(csv_filename)
    logger.info('Carregando arquivo CSV: %s', csv_path)

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f'Arquivo não encontrado: {csv_path}')

    df = pd.read_csv(csv_path)
    logger.info('Arquivo carregado com sucesso: %d linhas e %d colunas', len(df), len(df.columns))
    return df


def validar_dados(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError('O arquivo CSV está vazio')

    required_columns = {'Name', 'Card_Limit'}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError('Colunas obrigatórias ausentes: ' + ', '.join(sorted(missing_columns)))

    logger.info('Validação concluída. Colunas obrigatórias presentes: %s', ', '.join(sorted(required_columns)))

    empty_names = df['Name'].isna().sum()
    if empty_names > 0:
        logger.warning('Existem %d registros sem nome definido', empty_names)

    missing_limits = df['Card_Limit'].isna().sum()
    if missing_limits > 0:
        logger.warning('Existem %d registros com Card_Limit ausente', missing_limits)


def gerar_mensagem_marketing(linha: pd.Series) -> str:
    nome = linha.get('Name', 'Cliente')
    limite = linha.get('Card_Limit', 0)

    if pd.isna(limite):
        limite = 0

    if limite > 5000:
        return (
            f'Olá, {nome}! Seu perfil premium permite acessar investimentos exclusivos '
            'com boas taxas de retorno. Vamos conversar sobre renda fixa diferenciada?'
        )
    if limite > 2500:
        return (
            f'Olá, {nome}! Seu limite está muito bom. Que tal aproveitar produtos de investimento '
            'com liquidez e estabilidade para proteger seu patrimônio?'
        )

    return (
        f'Olá, {nome}! Comece já a construir seu futuro com opções de investimento '
        'acessíveis e um plano financeiro adaptado ao seu perfil.'
    )


def classificar_segmento(limite: float) -> str:
    if limite > 5000:
        return 'Premium'
    if limite > 2500:
        return 'Intermediário'
    return 'Acessível'


def resumo_segmentos(df: pd.DataFrame) -> pd.DataFrame:
    counts = df['Segmento'].value_counts().rename_axis('Segmento').reset_index(name='Contagem')
    logger.info('Resumo de segmentos:')
    logger.info('\n%s', counts)
    return counts


def transformar_dados(df: pd.DataFrame) -> pd.DataFrame:
    logger.info('Convertendo coluna Card_Limit para valores numéricos')
    if 'Card_Limit' in df.columns:
        df['Card_Limit'] = pd.to_numeric(df['Card_Limit'], errors='coerce').fillna(0)
    else:
        df['Card_Limit'] = 0

    df['Segmento'] = df['Card_Limit'].apply(classificar_segmento)
    df['News_Message'] = df.apply(gerar_mensagem_marketing, axis=1)
    df['Sugestao_Produto'] = df['Segmento'].map(
        {
            'Premium': 'Fundos exclusivos',
            'Intermediário': 'CDBs e previdência',
            'Acessível': 'Planos de investimento para iniciantes',
        }
    )

    logger.info('Transformação concluída: colunas Segmento, News_Message e Sugestao_Produto adicionadas')
    return df


def salvar_resultado(df: pd.DataFrame, filename: str) -> None:
    output_path = resolve_path(filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info('Arquivo final salvo em: %s', output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Pipeline ETL para SDW2023 CSV')
    parser.add_argument('--input', '-i', default='SDW2023.csv', help='Arquivo CSV de entrada')
    parser.add_argument('--output', '-o', default='SDW2023_atualizado.csv', help='Arquivo CSV de saída')
    parser.add_argument('--log', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='Nível de log')
    parser.add_argument('--sample', type=int, default=5, help='Número de linhas de amostra a exibir')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging(args.log)

    logger.info('Iniciando o pipeline de extração-transformação-carregamento')
    df = carregar_dados(args.input)
    validar_dados(df)

    logger.info('Exibindo amostra dos dados carregados')
    logger.info('\n%s', df.head(args.sample))

    df = transformar_dados(df)
    resumo_segmentos(df)

    logger.info('Exibindo amostra dos dados transformados')
    logger.info('\n%s', df[['Name', 'Card_Limit', 'Segmento', 'Sugestao_Produto', 'News_Message']].head(args.sample))

    salvar_resultado(df, args.output)
    logger.info('Pipeline finalizado com sucesso')


logger = logging.getLogger(__name__)


if __name__ == '__main__':
    try:
        main()
    except (FileNotFoundError, ValueError) as error:
        logger.error(error)
        sys.exit(1)
    except Exception as error:
        logger.exception('Erro inesperado durante a execução do pipeline')
        sys.exit(1)
