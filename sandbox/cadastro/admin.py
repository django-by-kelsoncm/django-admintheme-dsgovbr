from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import messages

from dsgovbr.admin import ObjectToolSpec, InstanceActionSpec
from dsgovbr.admin.import_export import DSGovBrModelAdmin
from .models import Orgao, Servidor, Documento, Servico


class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 1


class ServidorInline(admin.StackedInline):
    model = Servidor
    extra = 1
    show_change_link = True


@admin.register(Orgao)
class OrgaoAdmin(DSGovBrModelAdmin):
    list_display = ("sigla", "nome", "ativo", "data_criacao", "acoes_customizadas")
    list_filter = ("ativo", "data_criacao")
    search_fields = ("nome", "sigla", "descricao")
    inlines = [ServidorInline]

    # Ações Customizadas no topo da Lista (Object Tools)
    def get_object_tool_actions(self, request) -> list:
        # Retorna as ações padrões (Import/Export) + nossa ação customizada
        actions = super().get_object_tool_actions(request)
        actions.append(
            ObjectToolSpec(
                label="Relatório PDF",
                handler="gerar_relatorio",
                icon="fas fa-file-pdf",
                css_class="btn-secondary",
                admin=self,
            )
        )
        return actions

    # Implementação do Handler da Ação do Topo
    def gerar_relatorio(self, request):
        # Apenas demonstração retornando um texto simples
        return HttpResponse(
            "<h2>Relatório PDF de Órgãos Gerado com Sucesso!</h2><p>Esta é uma view customizada simulando a geração de um relatório.</p>"
        )

    # View customizada no nível de Instância (rota automática gerada pelo DSGovBrModelAdmin)
    def historico_customview(self, request, object_id):
        orgao = self.get_object(request, object_id)
        return HttpResponse(
            f"<h2>Histórico de Auditoria do Órgão: {orgao.sigla}</h2><p>Aqui você pode listar logs ou auditorias de alterações.</p>"
        )

    # Coluna customizada na listagem para facilitar navegação
    def acoes_customizadas(self, obj):
        url = reverse("admin:cadastro_orgao_historico", args=[obj.pk])
        return format_html(
            '<a class="button" href="{}"><i class="fas fa-history"></i> Auditoria</a>',
            url,
        )

    acoes_customizadas.short_description = "Ações"


@admin.register(Servidor)
class ServidorAdmin(DSGovBrModelAdmin):
    list_display = ("nome", "orgao", "cargo", "email", "data_admissao")
    list_filter = ("orgao", "cargo", "data_admissao")
    search_fields = ("nome", "cpf", "email", "cargo")
    autocomplete_fields = ("orgao",)
    inlines = [DocumentoInline]

    # Ações no nível do Objeto individual (Instance Actions)
    instance_actions = [
        InstanceActionSpec(
            label="Visualizar Crachá",
            handler="visualizar_cracha",
            icon="fas fa-id-card",
            css_class="btn-primary",
        ),
        InstanceActionSpec(
            label="Enviar E-mail de Boas Vindas",
            handler="enviar_boas_vindas",
            icon="fas fa-paper-plane",
            css_class="btn-success",
        ),
    ]

    # Handlers para as ações de instância
    def visualizar_cracha_customview(self, request, object_id):
        servidor = self.get_object(request, object_id)
        content = f"""
        <html>
        <head>
            <title>Crachá Digital</title>
            <style>
                body {{ font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f0f2f5; }}
                .badge {{ border: 2px solid #00c012; border-radius: 8px; padding: 20px; background: white; width: 300px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
                .org {{ font-size: 14px; font-weight: bold; color: #1f305e; margin-bottom: 15px; text-transform: uppercase; }}
                .name {{ font-size: 20px; font-weight: bold; color: #333; margin: 10px 0; }}
                .role {{ font-size: 16px; color: #666; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="badge">
                <div class="org">{servidor.orgao.nome}</div>
                <div style="width:100px; height:100px; border-radius: 50%; background: #ccc; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 40px; color: white;">👤</div>
                <div class="name">{servidor.nome}</div>
                <div class="role">{servidor.cargo}</div>
                <div style="font-size: 11px; color: #999;">CPF: {servidor.cpf}</div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(content)

    def enviar_boas_vindas_customview(self, request, object_id):
        servidor = self.get_object(request, object_id)
        messages.success(
            request, f"E-mail de boas-vindas enviado com sucesso para {servidor.email}!"
        )
        # Redireciona de volta para a view de preview/visualização do servidor
        return redirect(reverse("admin:cadastro_servidor_preview", args=[object_id]))


@admin.register(Servico)
class ServicoAdmin(DSGovBrModelAdmin):
    list_display = ("nome", "url_portal", "publico_alvo")
    filter_horizontal = ("orgaos_envolvidos",)
    search_fields = ("nome", "publico_alvo")


@admin.register(Documento)
class DocumentoAdmin(DSGovBrModelAdmin):
    list_display = ("servidor", "tipo", "data_upload")
    list_filter = ("tipo", "data_upload")
