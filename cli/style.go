package cli

import "github.com/charmbracelet/lipgloss"

var (
	tableCellStyle = lipgloss.NewStyle().Padding(0, 1).Foreground(lipgloss.AdaptiveColor{
		Light: "15",
		Dark:  "7",
	})
	tableHeaderStyle = lipgloss.NewStyle().Padding(0, 1).Foreground(lipgloss.AdaptiveColor{
		Light: "12",
		Dark:  "4",
	}).Bold(true)
	activatedStateStyle = tableCellStyle.Foreground(lipgloss.AdaptiveColor{
		Light: "2",
		Dark:  "10",
	})
	suspendedStateStyle = tableCellStyle.Foreground(lipgloss.AdaptiveColor{
		Light: "1",
		Dark:  "9",
	})
	stagedStateStyle = tableCellStyle.Foreground(lipgloss.AdaptiveColor{
		Light: "3",
		Dark:  "11",
	})
	idColStyle = tableCellStyle.Width(26)
	keyStyle   = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.AdaptiveColor{
		Light: "12",
		Dark:  "4",
	})
	valueStyle = lipgloss.NewStyle().Foreground(lipgloss.AdaptiveColor{
		Light: "15",
		Dark:  "7",
	})
)
