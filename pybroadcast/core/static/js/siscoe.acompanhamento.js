/*
 Executa os eventos quando a página carregar.
 */
function populaTabelas() {
	var martelada = ['Dou-lhe uma', 'Negociado', 'Retirado','Em Leilão'];
	var modos = ['C (+)', 'V (+)'];
	
	for (var i = 0; i < 20; i++) {
		var indexMartelada = Math.floor(Math.random()*4);
		var indexModos = Math.floor(Math.random()*2);

		var linhaFormatada = 
				martelada[indexMartelada]=='Dou-lhe uma'?'<tr class="warning">':
				martelada[indexMartelada]=='Negociado'  ?'<tr class="success">':
				martelada[indexMartelada]=='Retirado'   ?'<tr class="danger">':
				'<tr>';
		var icone = '<i class="fa fa-fw fa-lg ' +
				(martelada[indexMartelada]=='Dou-lhe uma'?'fa-warning':
				martelada[indexMartelada]=='Negociado'   ?'fa-legal':
				martelada[indexMartelada]=='Retirado'    ?'fa-ban':
				'fa-clock-o') + '"/>';
		// Adiciona registros de leilão
		$('#leilao tbody').append(
			linhaFormatada +
				'<td>9999/9999</td>'+
				'<td>'+ icone + ' ' + martelada[indexMartelada++] +'</td>'+
				'<td class="text-right">999.999,99</td>'+
				'<td class="text-right">999.999,99</td>'+
				'<td class="text-center">99%</td>'+
				'<td class="text-right">999.999.999,99</td>'+
				'<td class="text-right">999.999.999,99</td>'+
				'<td class="text-center">99%</td>'+
				'<td class="text-center">'+ modos[indexModos++]  +'</td>'+
			'</tr>'
		);

		// Adiciona registros de lance
		$('#lance tbody').append(
			'<tr style="color: '+ (i<10 ? 'blue' : i<12 ? 'red' : 'darkGray') +'">'+
				'<td>BNM</td>'+
				'<td class="text-right">0,0000</td>'+
			'</tr>'
		);
	}
}

function carregaSlideMensagem() {
	// Implementar futuramente
}

function adicionaInformacoesLote() {
	$('#leilao tr').click(function() {
		console.log($(this).next());

		var info = 
		$('<tr class="active">'
			+'<td colspan="2">Operação: Compra</td>'
			+'<td colspan="7">Produto: ARROZ > LONGO FINO > EM CASCA > RÃOS INTEIROS 34-36</td>'
		+'</tr>'
		+'<tr class="active">'
			+'<td colspan="5">Unidade de Comercialização: SACO JUTA 50kg (SACO JUTA 50 kg)</td>'
			+'<td>Safra: 9999/9999</td>'
			+'<td colspan="3">Valor de Comercialização: 99,99</td>'
		+'</tr>');

		$(this).after(info);
		$(this).unbind();
	})
}

// Popula a tabela de leilão com informações repetidas
$(document).ready(function() {
	populaTabelas();
	carregaSlideMensagem();
	adicionaInformacoesLote();
})