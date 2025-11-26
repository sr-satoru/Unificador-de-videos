# 🧹 Sistema de Limpeza Inteligente

## 📋 Visão Geral

Sistema automático de limpeza de arquivos que mantém o servidor organizado e otimizado, removendo arquivos desnecessários em intervalos inteligentes.

## 🎯 Funcionalidades

### ⏰ **Limpeza Automática por Tempo**

1. **📁 Uploads (5 segundos)**
   - Arquivos originais são removidos após processamento
   - Mantém apenas os vídeos processados

2. **🎬 Vídeos Processados (1 minuto)**
   - Vídeos individuais são removidos após criação do ZIP
   - Mantém apenas o arquivo ZIP

3. **📦 ZIPs (10 minutos)**
   - Arquivos ZIP são removidos após download
   - Limpeza completa do job

### 🔄 **Verificação Contínua**
- **Intervalo**: A cada 30 segundos
- **Background**: Executa automaticamente
- **Logs**: Todas as operações são registradas

## 🗄️ **Banco de Dados SQLite**

### **Tabelas**

#### `files` - Rastreamento de Arquivos
```sql
- id: TEXT (PK) - ID único do arquivo
- original_name: TEXT - Nome original
- file_path: TEXT - Caminho do arquivo
- size: INTEGER - Tamanho em bytes
- upload_time: TIMESTAMP - Data de upload
- status: TEXT - Status do arquivo
- job_id: TEXT (FK) - ID do job relacionado
- processed_time: TIMESTAMP - Data de processamento
- output_path: TEXT - Caminho do arquivo processado
```

#### `jobs` - Rastreamento de Jobs
```sql
- id: TEXT (PK) - ID único do job
- status: TEXT - Status do job
- progress: INTEGER - Progresso (0-100)
- started_at: TIMESTAMP - Data de início
- completed_at: TIMESTAMP - Data de conclusão
- zip_path: TEXT - Caminho do ZIP
- zip_created_at: TIMESTAMP - Data de criação do ZIP
- settings: TEXT - Configurações do job
- error_message: TEXT - Mensagem de erro
```

#### `cleanup_log` - Log de Operações
```sql
- id: INTEGER (PK) - ID único
- operation: TEXT - Tipo de operação
- file_path: TEXT - Caminho do arquivo
- job_id: TEXT - ID do job
- timestamp: TIMESTAMP - Data da operação
- success: BOOLEAN - Sucesso da operação
- error_message: TEXT - Mensagem de erro
```

## 🚀 **APIs de Gerenciamento**

### **GET /cleanup/stats**
```json
{
  "database_stats": {
    "total_files": 150,
    "files_by_status": {
      "uploaded": 50,
      "processing": 10,
      "completed": 90
    },
    "total_jobs": 75,
    "jobs_by_status": {
      "processing": 5,
      "completed": 70
    }
  },
  "storage_usage": {
    "uploads_size_mb": 250.5,
    "outputs_size_mb": 1200.3,
    "temp_size_mb": 15.2,
    "total_size_mb": 1466.0
  },
  "cleanup_settings": {
    "upload_cleanup_delay": 5,
    "zip_cleanup_delay": 10,
    "processed_video_cleanup_delay": 1,
    "cleanup_interval": 30
  }
}
```

### **POST /cleanup/manual**
- Força uma limpeza manual imediata
- Útil para testes e manutenção

### **POST /cleanup/force/{job_id}**
- Força limpeza de todos os arquivos de um job específico
- Útil para limpeza de jobs com problemas

## 🔧 **Configurações**

### **Timers (em minutos)**
```python
upload_cleanup_delay = 5        # Uploads: 5 segundos
zip_cleanup_delay = 10          # ZIPs: 10 minutos  
processed_video_cleanup_delay = 1  # Vídeos: 1 minuto
cleanup_interval = 30           # Verificação: 30 segundos
```

### **Personalização**
- Todos os timers são configuráveis
- Pode ser ajustado via variáveis de ambiente
- Logs detalhados para monitoramento

## 📊 **Monitoramento**

### **Métricas Disponíveis**
- Total de arquivos no sistema
- Uso de armazenamento por pasta
- Status de jobs e arquivos
- Histórico de operações de limpeza
- Taxa de sucesso das operações

### **Logs**
- Todas as operações são registradas
- Erros são capturados e logados
- Histórico completo de limpeza
- Estatísticas de performance

## 🎯 **Benefícios**

### **💾 Otimização de Espaço**
- Remove arquivos desnecessários automaticamente
- Mantém apenas arquivos essenciais
- Reduz uso de armazenamento

### **🔒 Segurança**
- Remove arquivos temporários
- Limpa dados sensíveis automaticamente
- Previne acúmulo de arquivos

### **⚡ Performance**
- Mantém sistema limpo e rápido
- Reduz overhead de armazenamento
- Otimiza operações de I/O

### **📈 Escalabilidade**
- Sistema inteligente que se adapta
- Configurável para diferentes ambientes
- Monitoramento completo

## 🧪 **Testes**

### **Script de Teste**
```bash
python test_cleanup_system.py
```

### **Verificações**
- Estatísticas de limpeza
- Uso de armazenamento
- Operações de limpeza manual
- Status do banco de dados

## 🚨 **Troubleshooting**

### **Problemas Comuns**
1. **Arquivos não são limpos**
   - Verificar logs de erro
   - Confirmar permissões de arquivo
   - Verificar status no banco de dados

2. **Banco de dados corrompido**
   - Backup automático recomendado
   - Recriação do banco se necessário

3. **Performance lenta**
   - Ajustar intervalos de limpeza
   - Verificar uso de armazenamento
   - Monitorar logs de operações

## 🔮 **Futuras Melhorias**

- [ ] Limpeza baseada em uso de espaço
- [ ] Compressão de arquivos antigos
- [ ] Backup automático do banco
- [ ] Interface web para monitoramento
- [ ] Alertas por email/Slack
- [ ] Métricas avançadas de performance
