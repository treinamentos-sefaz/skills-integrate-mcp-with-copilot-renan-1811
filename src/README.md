# API de Atividades da Mergington High School

Uma aplicação FastAPI super simples que permite aos estudantes visualizar e se inscrever em atividades extracurriculares.

## Funcionalidades

- Visualizar todas as atividades extracurriculares disponíveis
- Inscrever-se em atividades

## Primeiros Passos

1. Instale as dependências:

   ```
   pip install fastapi uvicorn
   ```

2. Execute a aplicação:

   ```
   python app.py
   ```

3. Abra seu navegador e vá para:
   - Documentação da API: http://localhost:8000/docs
   - Documentação alternativa: http://localhost:8000/redoc

## Endpoints da API

| Método | Endpoint                                                          | Descrição                                                           |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Obter todas as atividades com seus detalhes e contagem atual de participantes |
| POST   | `/auth/login`                                                     | Iniciar sessão de professor com nome de usuário e senha             |
| POST   | `/auth/logout`                                                    | Encerrar a sessão de professor                                      |
| GET    | `/auth/me`                                                        | Consultar a sessão atual                                            |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Inscrever estudante (requer sessão de professor)                   |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Remover inscrição (requer sessão de professor)                  |

### Configuração do acesso de professores

Crie um hash de senha sem armazenar a senha em texto puro:

```sh
.venv/bin/python -c "from src.app import hash_password; print(hash_password(input('Senha do professor: ')))"
```

Crie `src/teachers.json` com o nome de usuário e o hash gerado:

```json
{
  "teachers": {
    "professor": "pbkdf2_sha256$310000$<salt>$<hash>"
  }
}
```

O arquivo local de credenciais é ignorado pelo Git. É possível definir outro caminho com `TEACHER_CREDENTIALS_FILE`. Para manter as sessões válidas após reiniciar o servidor, configure `SESSION_SECRET` com um segredo aleatório e persistente. Em produção com HTTPS, defina também `SESSION_COOKIE_SECURE=true`.

## Modelo de Dados

A aplicação usa um modelo de dados simples com identificadores significativos:

1. **Atividades** - Usa o nome da atividade como identificador:

   - Descrição
   - Cronograma
   - Número máximo de participantes permitidos
   - Lista de emails de estudantes que estão inscritos

2. **Estudantes** - Usa email como identificador:
   - Nome
   - Nível da série

Todos os dados são armazenados na memória, o que significa que os dados serão resetados quando o servidor reiniciar.
